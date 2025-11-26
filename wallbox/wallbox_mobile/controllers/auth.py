# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import jwt
import json
import logging
from datetime import datetime
from werkzeug.exceptions import BadRequest, Unauthorized
from odoo.exceptions import AccessDenied, ValidationError
from odoo import Command, SUPERUSER_ID, _
from odoo import http
from odoo.http import request, Response
from odoo.addons.web.controllers.utils import ensure_db
from odoo.addons.wallbox_mobile import utils

_logger = logging.getLogger(__name__)


class AuthController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    @http.route('/v1/auth/login', type='json', auth='none', methods=['POST'], csrf=False)
    def login(self, **kwargs):
        """User login endpoint"""
        ensure_db()
        try:
            data = json.loads(request.httprequest.data)
            email = data.get('email', '').strip()
            password = data.get('password', '').strip()
            device_token = data.get('device_token', '').strip()

            if not email or not password:
                return utils._error_response('VALIDATION_ERROR', _('Email and password are required'))

            # Authenticate user
            try:
                credential = {'login': email, 'password': password, 'type': 'password'}
                auth_result = request.session.authenticate(request.db, credential)

                if not auth_result or not isinstance(auth_result, dict) or not auth_result.get('uid'):
                    return utils._error_response('INVALID_CREDENTIALS', _('Invalid credentials'))

                uid = auth_result['uid']
                user = request.env['res.users'].sudo().browse(uid)

                if not user.exists():
                    return utils._error_response('INVALID_CREDENTIALS', _('User account not found'))

                if not user.active:
                    return utils._error_response('INVALID_CREDENTIALS', _('Account is inactive'))

            except AccessDenied:
                return utils._error_response('INVALID_CREDENTIALS', _('Invalid email or password'))
            except Exception as e:
                _logger.error("Authentication error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # Handle device token
            if device_token:
                try:
                    self._update_device_token(user, device_token)
                except Exception as e:
                    _logger.warning("Device token update failed: %s", str(e))

            # Generate tokens
            tokens = utils._generate_jwt_tokens(user)
            user.jwt_token = tokens['token']  # Store only access token

            result = {
                'status': True,
                'token': tokens['token'],
                'tokenExp': tokens['tokenExp'],
                'refresh': tokens['refresh'],
                'user': utils._get_user_data(user)
            }

            utils._log_api_error(api_name="/v1/auth/login", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except Exception as e:
            _logger.error("Login failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', _('Login failed'))

    @http.route('/v1/auth/register', type='json', auth='none', methods=['POST'], csrf=False)
    def register(self, **kwargs):
        """User registration endpoint"""
        ensure_db()
        try:
            data = json.loads(request.httprequest.data)
            email = data.get('email')
            password = data.get('password')
            name = data.get('name')
            phone = data.get('phone')
            device_token = data.get('device_token')

            if not all([email, password, name]):
                return utils._error_response('VALIDATION_ERROR', _('Name, email and password are required'))

            # Check for existing user
            existing_user = request.env['res.users'].with_user(SUPERUSER_ID).search(
                [('login', '=', email)], limit=1)
            if existing_user:
                return utils._error_response('EMAIL_ALREADY_REGISTERED', _('Email already registered'))

            # Create user
            try:
                company = request.env['res.company'].sudo().search([], limit=1)
                user_vals = {
                    'name': name,
                    'login': email,
                    'email': email,
                    'password': password,
                    'wallbox_user': True,
                    'company_id': company.id,
                    'company_ids': [Command.set(company.ids)],
                    'groups_id': [
                        Command.set([
                            request.env.ref('base.group_user').id,
                            request.env.ref('sales_team.group_sale_salesman').id,
                            request.env.ref('wallbox_integration.group_wallbox_user').id
                        ])
                    ],
                }
                if phone:
                    user_vals['phone'] = phone

                user = request.env['res.users'].with_context(
                    no_reset_password=True,
                    mail_create_nosubscribe=True
                ).with_user(SUPERUSER_ID).create(user_vals)
                request.env.cr.commit()

                if not user:
                    return utils._error_response('INTERNAL_ERROR', _('User creation failed'))

                # Handle device token
                if device_token:
                    try:
                        self._update_device_token(user, device_token)
                    except Exception as e:
                        _logger.warning("Device token registration failed: %s", str(e))

                # Generate tokens
                tokens = utils._generate_jwt_tokens(user)
                user.jwt_token = tokens['token']

                # Send Notification on mobile app of registrade user.
                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(user, 'New user registration completed.')

                result = {
                    'status': True,
                    'token': tokens['token'],
                    'tokenExp': tokens['tokenExp'],
                    'refresh': tokens['refresh'],
                    'user': utils._get_user_data(user)
                }

                utils._log_api_error(api_name="/v1/auth/register", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except Exception as e:
                _logger.error("Registration failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Registration error: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/auth/me', type='http', auth='none', methods=['GET'], csrf=False)
    def auth_me(self):
        """Get authenticated user profile"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            user_data = utils._get_user_data(user)

            utils._log_api_error(api_name="/v1/auth/me", error_code="SUCCESS", error_description="No Error", json_parameters=user_data, user=user)
            
            return self._json_response({
                'status': True,
                'result': user_data
            })

        except Exception as e:
            _logger.error("Failed to fetch profile: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/auth/update-profile', type='json', auth='none', methods=['PATCH'], csrf=False)
    def update_profile(self, **kwargs):
        """Update authenticated user profile (partial updates)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            if not data:
                return utils._error_response('INVALID_DATA', 'No data received')

            # Prepare update data for user and partner
            user_vals = {}
            partner_vals = {}

            # Only allow specific fields to be updated
            if 'name' in data and data['name']:
                user_vals['name'] = data['name'].strip()

            # Partner fields (partial updates)
            if 'phone' in data:
                partner_vals['phone'] = data['phone'].strip() if data['phone'] else False
            if 'mobile' in data:
                partner_vals['mobile'] = data['mobile'].strip() if data['mobile'] else False
            if 'street' in data:
                partner_vals['street'] = data['street'].strip() if data['street'] else False
            if 'street2' in data:
                partner_vals['street2'] = data['street2'].strip() if data['street2'] else False
            if 'city' in data:
                partner_vals['city'] = data['city'].strip() if data['city'] else False
            if 'zip' in data:
                partner_vals['zip'] = data['zip'].strip() if data['zip'] else False
            if 'state_id' in data:
                partner_vals['state_id'] = int(data['state_id']) if data['state_id'] else False
            if 'country_id' in data:
                partner_vals['country_id'] = int(data['country_id']) if data['country_id'] else False

            # Update records
            try:
                if user_vals:
                    user.sudo().write(user_vals)
                if partner_vals:
                    user.partner_id.sudo().write(partner_vals)
            except ValidationError as e:
                _logger.error("Profile update validation error: %s", str(e))
                return utils._error_response('VALIDATION_ERROR', str(e))
            except Exception as e:
                _logger.error("Profile update failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # Send Notification on mobile app of registrade user.
            notification_model = request.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(user, 'Your Profile has been updated.')


            result = {
                'status': True,
                'message': 'Profile updated successfully',
                'user': utils._get_user_data(user)
            }

            utils._log_api_error(api_name="/v1/auth/update-profile", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except Exception as e:
            _logger.error("Profile update error: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/auth/refresh', type='json', auth='none', methods=['POST'], csrf=False)
    def auth_refresh(self):
        """Refresh access token"""
        try:
            data = json.loads(request.httprequest.data)
            refresh_token = data.get('refresh_token')
            if not refresh_token:
                return utils._error_response('VALIDATION_ERROR', _('Refresh token is required'))

            config = utils._get_jwt_config()
            try:
                payload = jwt.decode(refresh_token, config['secret'], algorithms=[config['algorithm']])
                if payload.get('type') != 'refresh':
                    return utils._error_response('TOKEN_INVALID', _('Invalid token type'))

                user_id = payload.get('user_id')
                user = request.env['res.users'].sudo().browse(user_id)

                if not user.exists() or not user.active:
                    return utils._error_response('INVALID_CREDENTIALS', _('User not found or inactive'))

                tokens = utils._generate_jwt_tokens(user)
                user.jwt_token = tokens['token']

                utils._log_api_error(api_name="/v1/auth/update-profile", error_code="SUCCESS", error_description="No Error", json_parameters=tokens, user=user)

                return utils._success_response(tokens)

            except jwt.ExpiredSignatureError:
                return utils._error_response('TOKEN_EXPIRED', _('Refresh token expired'))
            except jwt.InvalidTokenError:
                return utils._error_response('TOKEN_INVALID', _('Invalid refresh token'))
                
        except Exception as e:
            _logger.error("Token refresh failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', _('Token refresh failed'))

    @http.route('/v1/auth/logout', type='json', auth='none', methods=['POST'], csrf=False)
    def logout(self):
        """User logout endpoint"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # Clear tokens
            user.jwt_token = False

            # Clear device token if provided
            data = json.loads(request.httprequest.data)
            device_token = data.get('device_token')
            if device_token:
                request.env['wallbox.device.token'].sudo().search([
                    ('user_id', '=', user.id),
                    ('token', '=', device_token)
                ]).unlink()

            result = {
                'status': True,
                'message': 'Logged out'
            }

            utils._log_api_error(api_name="/v1/auth/logout", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except Unauthorized as e:
            return utils._error_response('TOKEN_INVALID', str(e))
        except Exception as e:
            _logger.error("Logout failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/auth/delete', type='json', auth='none', methods=['DELETE'], csrf=False)
    def auth_delete(self):
        """Delete user account"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # Archive user
            user.sudo().write({
                'active': False,
                # 'login': f'deleted_{user.id}_{datetime.now().strftime("%Y%m%d%H%M%S")}',
                'jwt_token': False
            })

            data = {
                'status': True,
                'message': 'Account deleted successfully'
            }

            utils._log_api_error(api_name="/v1/auth/delete", error_code="SUCCESS", error_description="No Error", json_parameters=data, user=user)

            return data

        except Unauthorized as e:
            return utils._error_response('TOKEN_INVALID', str(e))
        except Exception as e:
            _logger.error("Account deletion failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/auth/forgot-password', type='json', auth='none', methods=['POST'], csrf=False)
    def forgot_password(self):
        """Handle password reset request"""
        try:
            data = json.loads(request.httprequest.data)
            email = data.get('email')

            if not email:
                return utils._error_response('VALIDATION_ERROR', _('Email is required'))

            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user:
                return utils._error_response('RESOURCE_NOT_FOUND', _('No account found with this email'))

            if not user.email:
                return utils._error_response('VALIDATION_ERROR', _('User has no email address configured'))

            # Generate reset token and send email
            user.action_reset_password()

            result = {
                'status': True,
                'message': 'Password reset email sent',
            }

            utils._log_api_error(api_name="/v1/auth/forgot-password", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except Exception as e:
            _logger.error("Password reset failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/auth/change-password', type='json', auth='none', methods=['POST'], csrf=False)
    def change_password(self):
        """Authenticated user password update (requires old and new password)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            old_password = data.get('old_password', '').strip()
            new_password = data.get('new_password', '').strip()

            if not old_password or not new_password:
                return utils._error_response('VALIDATION_ERROR', _('Old and new password are required'))

            # Re-authenticate using old password
            try:
                # `authenticate()` returns False if invalid
                valid = request.session.authenticate(request.db, {'login': user.login, 'password': old_password, 'type': 'password'})
                if not valid:
                    return utils._error_response('INVALID_CREDENTIALS', _('Incorrect current password'))
            except AccessDenied:
                return utils._error_response('INVALID_CREDENTIALS', _('Incorrect current password'))

            # Update password
            try:
                user.sudo().write({'password': new_password})
            except Exception as e:
                _logger.error("Password update error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', _('Failed to update password'))

            # Send Notification on mobile app of registrade user.
            notification_model = request.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(user, 'Password updated successfully.')

            result = {
                'status': True,
                'message': _('Password updated successfully')
            }

            utils._log_api_error(api_name="/v1/auth/change-password", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except Exception as e:
            _logger.error("Change password failed: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', _('Password change failed'))

    def _update_device_token(self, user, device_token):
        """Update device token for push notifications"""
        DeviceToken = request.env['wallbox.device.token'].sudo()
        existing = DeviceToken.search([
            ('user_id', '=', user.id),
            ('token', '=', device_token)
        ])
        if not existing:
            DeviceTokenOBJ = DeviceToken.create({
                'user_id': user.id,
                'token': device_token,
                'platform': 'expo'
            })
