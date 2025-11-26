# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
from odoo.addons.wallbox_mobile import utils
from odoo.addons.web.controllers.utils import ensure_db
from odoo.exceptions import ValidationError, AccessError

_logger = logging.getLogger(__name__)

class ChargingRequestController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    # ============================================
    # CHARGING REQUEST CREATION ENDPOINTS
    # ============================================

    @http.route('/v1/charging/requests/create', type='json', auth='none', methods=['POST'], csrf=False)
    def create_charging_request(self, **post):
        """Create a new charging request"""
        ensure_db()
        try:
            # 1. Parse and validate input
            try:
                data = json.loads(request.httprequest.data)
                wallbox_serial = data.get('wallbox_serial_id')
                vehicle_id = data.get('vehicle_id')
                scheduled_date = data.get('service_scheduled_date')

                if not wallbox_serial or not vehicle_id:
                    return utils._error_response('VALIDATION_ERROR', 
                        'Wallbox serial and vehicle ID are required')

            except ValueError:
                return utils._error_response('VALIDATION_ERROR', 'Invalid request data')

            # 2. Authenticate user
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # 3. Validate wallbox
            try:
                wallbox_serial_id = request.env['stock.lot.report'].sudo().search([
                    ('lot_id.name', '=', wallbox_serial)
                ], limit=1)
                charging_station = request.env['charging.station'].sudo().search([
                    ('charger_id', '=', wallbox_serial)
                ], limit=1)

                _logger.info("Wallbox wallbox_serial_id === : %s", str(wallbox_serial_id))
                _logger.info("Wallbox charging_station === : %s", str(charging_station))

                if not wallbox_serial_id or not charging_station:
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Wallbox not found')
            except Exception as e:
                _logger.error("Wallbox lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', 'Wallbox validation failed')

            # 4. Check user permissions
            try:
                is_owner = (user.partner_id == charging_station.owner_id)
                is_monthly_user = (user.partner_id.id in charging_station.allowed_partner_ids.ids)

                if (is_owner or is_monthly_user) and not scheduled_date:
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Scheduled date is required for owners/monthly users')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Create request
            try:
                vals = {
                    'wallbox_serial_id': wallbox_serial_id.id,
                    'vehicle_id': vehicle_id,
                    'request_user_id': user.partner_id.id,
                    'request_status': 'draft',
                }

                if is_owner or is_monthly_user:
                    vals['service_scheduled_date'] = scheduled_date

                charging_request = request.env['request.charging'].with_user(user).create(vals)

                response_data = charging_request._get_prepared_charging_request_data()

                # Send Notification on mobile app for charging request created.
                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(user, 'Charging request created successfully.')

                result = {
                    'status': True,
                    'message': 'Charging request created successfully',
                    'charging_request': response_data
                }

                utils._log_api_error(api_name="/v1/charging/requests/create", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except Exception as e:
                _logger.error("Request creation failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in charging request: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/charging/requests/<int:request_id>/update', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_charging_request(self, request_id, **post):
        """Update an existing charging request"""
        ensure_db()
        try:
            # 1. Parse and validate input
            try:
                data = json.loads(request.httprequest.data)
                update_fields = {
                    'vehicle_id': data.get('vehicle_id'),
                    'service_scheduled_date': data.get('service_scheduled_date'),
                    'charging_power': data.get('charging_power'),
                    'reservation_requested': data.get('reservation_requested'),
                    'reservation_date': data.get('reservation_date'),
                    'service_notes': data.get('service_notes'),
                }

                # Remove None values to avoid clearing fields unintentionally
                update_fields = {k: v for k, v in update_fields.items() if v is not None}

                if not update_fields:
                    return utils._error_response('VALIDATION_ERROR', 'No valid fields provided for update')

            except ValueError:
                return utils._error_response('VALIDATION_ERROR', 'Invalid request data')

            # 2. Authenticate user
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # 3. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].with_user(user).browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Validate user permissions
            try:
                if user.partner_id != charging_request.request_user_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only requesting user can update the request')

                # Additional validation based on request status
                if charging_request.request_status not in ('draft', 'approved'):
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Request can only be updated in draft or approved status')

                # Validate vehicle exists if being updated
                if 'vehicle_id' in update_fields:
                    vehicle = request.env['user.vehicle'].sudo().browse(update_fields['vehicle_id'])
                    if not vehicle.exists():
                        return utils._error_response('RESOURCE_NOT_FOUND', 'Vehicle not found')

            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Process the update
            try:
                # Special handling for scheduled date if request is approved
                if 'service_scheduled_date' in update_fields and charging_request.request_status == 'approved':
                    # For approved requests, changing schedule date should reset status to approved
                    charging_request.with_user(user).write({
                        'service_scheduled_date': update_fields['service_scheduled_date'],
                        # 'request_status': 'approved'  # Reset from scheduled back to approved
                    })
                else:
                    charging_request.with_user(user).write(update_fields)

                # Get updated request data
                response_data = charging_request._get_prepared_charging_request_data()

                result = {
                    'status': True,
                    'message': 'Charging request updated successfully',
                    'charging_request': response_data
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/update", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except ValidationError as e:
                _logger.error("Validation error during update: %s", str(e))
                return utils._error_response('VALIDATION_ERROR', str(e))
            except Exception as e:
                _logger.error("Update processing failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in request update: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    # ============================================
    # APPROVAL FLOW ENDPOINTS (FOR WALLBOX OWNERS)
    # ============================================

    @http.route('/v1/charging/requests/<int:request_id>/request', type='json', auth='none', methods=['POST'], csrf=False)
    def request_charging(self, request_id, **post):
        """Submit charging request for approval"""
        ensure_db()
        try:
            # 1. Authenticate user
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # 2. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].sudo().browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 3. Validate user permissions
            try:
                # Check if user is the requester
                if user.partner_id != charging_request.request_user_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only requesting user can submit for approval')

                # Check if request is in draft status
                if charging_request.request_status != 'draft':
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Only draft requests can be submitted for approval')

                # Check if user is guest (not owner/monthly user)
                charging_station = charging_request.charging_station_id
                if (user.partner_id == charging_station.owner_id or 
                    user.partner_id.id in charging_station.allowed_partner_ids.ids):
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Owners and monthly users don\'t need approval')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Process the request
            try:
                charging_request.with_user(user).action_request_charging()

                # Notify wallbox owner
                if charging_station.owner_id:
                    try:

                        # Send Notification on mobile app for charging request is waiting for approval.
                        notification_model = request.env['push.notification'].sudo()
                        success = notification_model.send_expo_notification(charging_request.wallbox_owner_id.user_id or charging_request.wallbox_owner_id.user_ids[0], 'New charging request awaiting your approval.')

                        charging_request._send_notification(
                            "New charging request awaiting your approval",
                            charging_station.owner_id
                        )
                    except Exception as e:
                        _logger.warning("Notification failed: %s", str(e))

                response_data = charging_request._get_prepared_charging_request_data()

                result = {
                    'status': True,
                    'message': 'Charging request submitted for approval',
                    'charging_request': response_data
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/request", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except Exception as e:
                _logger.error("Request processing failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in request submission: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/charging/requests/<int:request_id>/approve', type='json', auth='none', methods=['POST'], csrf=False)
    def approve_charging_request(self, request_id, **post):
        """Approve charging request"""
        ensure_db()
        try:
            # 1. Parse and validate input
            try:
                data = json.loads(request.httprequest.data)
                payment_method = data.get('payment_method', '').strip().lower()

                if not payment_method or payment_method not in ['cash', 'pre-authorize']:
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Valid payment method is required (cash or pre-authorize)')
            except ValueError:
                return utils._error_response('VALIDATION_ERROR', 'Invalid request data')

            # 2. Authenticate user
            try:
                user = utils._get_user_and_validate_request_authentication()
                if isinstance(user, dict) and user.get('error'):
                    return user
            except Unauthorized as e:
                return utils._error_response('TOKEN_INVALID', str(e))

            # 3. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].sudo().browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Validate owner permissions
            try:
                if user.partner_id != charging_request.wallbox_owner_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only wallbox owner can approve requests')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Process approval
            try:
                # Set payment method before approval
                charging_request.write({'payment_method': payment_method})
                charging_request.with_user(user).action_approve()
                response_data = charging_request._get_prepared_charging_request_data()

                # Send notification on mobile to requested user for charging request is approved.
                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(charging_request.request_user_id.user_id or charging_request.request_user_id.user_ids[0], 'Charging request approved successfully.')

                result = {
                    'status': True,
                    'message': 'Charging request approved successfully',
                    'charging_request': response_data,
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/approve", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except Exception as e:
                _logger.error("Approval processing failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in request approval: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    # ============================================
    # SCHEDULING ENDPOINTS
    # ============================================

    @http.route('/v1/charging/requests/<int:request_id>/schedule', type='json', auth='none', methods=['POST'], csrf=False)
    def schedule_charging(self, request_id, **post):
        """Schedule charging session"""
        ensure_db()
        try:
            # 1. Parse and validate input
            try:
                data = json.loads(request.httprequest.data)
                scheduled_date = data.get('service_scheduled_date')

                if not scheduled_date:
                    return utils._error_response('VALIDATION_ERROR', 'Scheduled date is required')
            except ValueError:
                return utils._error_response('VALIDATION_ERROR', 'Invalid request data')

            # 2. Authenticate user
            try:
                user = utils._get_user_and_validate_request_authentication()
                if isinstance(user, dict) and user.get('error'):
                    return user
            except Unauthorized as e:
                return utils._error_response('TOKEN_INVALID', str(e))

            # 3. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].sudo().browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Validate user permissions
            try:
                if user.partner_id != charging_request.request_user_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only requesting user can schedule charging')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Validate guest user requirements
            try:
                is_guest = (user.partner_id != charging_request.wallbox_owner_id and 
                           user.partner_id.id not in charging_request.charging_station_id.allowed_partner_ids.ids)
                
                if is_guest:
                    if charging_request.request_status != 'approved':
                        return utils._error_response('VALIDATION_ERROR', 
                                                  'Guest users must be approved before scheduling')
                    
                    if (charging_request.payment_method == 'pre-authorize' and 
                        charging_request.transaction_state != 'authorized'):
                        return utils._error_response('VALIDATION_ERROR', 
                                                  'Payment must be authorized before scheduling')
            except Exception as e:
                _logger.error("Guest validation error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 6. Process scheduling
            try:
                vals = {
                    'service_scheduled_date': scheduled_date
                }
                charging_request.write(vals)
                charging_request.with_user(user).action_schedule_charging()

                response_data = charging_request._get_prepared_charging_request_data()

                # Send notification on mobile to requested user for charging request is approved.
                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(charging_request.request_user_id.user_id or charging_request.request_user_id.user_ids[0], 'Charging request scheduled sucessfully.')

                result = {
                    'status': True,
                    'message': 'Charging request scheduled sucessfully',
                    'charging_request': response_data,
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/schedule", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

                return result

            except Exception as e:
                _logger.error("Scheduling processing failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in scheduling: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    # ||============================================
    # || CHARGING SESSION CONTROL ENDPOINTS ========
    # ||============================================

    @http.route('/v1/charging/requests/<int:request_id>/start', type='json', auth='none', methods=['POST'], csrf=False)
    def start_charging(self, request_id, **post):
        """Start charging session"""
        ensure_db()
        try:
            # 1. Authenticate user
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # 2. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].sudo().browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 3. Validate user permissions
            try:
                if user.partner_id != charging_request.request_user_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only requesting user can start charging')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Validate request status
            # try:
            #     if charging_request.request_status != 'scheduled':
            #         return utils._error_response('VALIDATION_ERROR', 
            #                                   'Cannot start charging - request not in scheduled status')
            # except Exception as e:
            #     _logger.error("Status validation error: %s", str(e))
            #     return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Start charging session
            try:
                result = charging_request.with_user(user).action_start_charging()

                response_data = charging_request._get_prepared_charging_request_data()

                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(charging_request.request_user_id.user_id or charging_request.request_user_id.user_ids[0], 'Start charging command has been sent to wallbox.')

                data = {
                    'status': True,
                    'message': 'Start charging command has been sent to wallbox.',
                    'charging_request': response_data,
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/start", error_code="SUCCESS", error_description="No Error", json_parameters=data, user=user)

                return data

            except Exception as e:
                _logger.error("Charging start failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in charging start: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/charging/requests/<int:request_id>/complete', type='json', auth='none', methods=['POST'], csrf=False)
    def complete_charging(self, request_id, **post):
        """Complete charging session"""
        ensure_db()
        try:
            # 1. Authenticate user
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            # 2. Validate charging request exists
            try:
                charging_request = request.env['request.charging'].sudo().browse(request_id)
                if not charging_request.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found')
            except Exception as e:
                _logger.error("Request lookup error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 3. Validate user permissions
            try:
                if user.partner_id != charging_request.request_user_id:
                    return utils._error_response('ACCESS_DENIED', 
                                              'Only requesting user can complete charging')
            except Exception as e:
                _logger.error("Permission check error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 4. Validate request status
            try:
                if charging_request.request_status != 'in_progress':
                    return utils._error_response('VALIDATION_ERROR', 
                                              'Cannot complete charging - request not in progress')
            except Exception as e:
                _logger.error("Status validation error: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

            # 5. Complete charging session
            try:
                result = charging_request.with_user(user).action_complete_charging()

                response_data = charging_request._get_prepared_charging_request_data()

                # Mobile Notification
                notification_model = request.env['push.notification'].sudo()
                success = notification_model.send_expo_notification(charging_request.request_user_id.user_id or charging_request.request_user_id.user_ids[0], 'Stop charging command has been sent to wallbox.')

                data = {
                    'status': True,
                    'message': 'Stop charging command has been sent to wallbox.',
                    'charging_request': response_data,
                }

                utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/complete", error_code="SUCCESS", error_description="No Error", json_parameters=data, user=user)

                return data

            except Exception as e:
                _logger.error("Charging completion failed: %s", str(e))
                return utils._error_response('INTERNAL_ERROR', str(e))

        except Exception as e:
            _logger.error("Unexpected error in charging completion: %s", str(e), exc_info=True)
            return utils._error_response('INTERNAL_ERROR', str(e))

    # ============================================
    # STATUS CHECK ENDPOINTS
    # ============================================

    @http.route('/v1/charging/requests/<int:request_id>/status', type='http', auth='none', methods=['GET'], csrf=False)
    def get_charging_status(self, request_id, **kwargs):
        """Get charging request status"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            charging_request = request.env['request.charging'].with_user(user).browse(request_id)

            if not charging_request.exists():
                return self._json_response(
                    utils._error_response('RESOURCE_NOT_FOUND', 'Charging request not found'),
                    404
                )

            response_data = {
                'request_status': charging_request.request_status,
                'can_start': charging_request.can_start_charging,
                'can_complete': charging_request.request_status == 'in_progress',
                'energy_consumed': charging_request.energy_consumed or 0,
                'payment_status': charging_request.transaction_state or 'pending',
                'payment_link': charging_request.payment_link if getattr(charging_request, 'visible_payment_link_btn', False) else None,
                'charging_station_status': charging_request.charging_station_id.status,
            }

            result = {
                'status': True,
                'charging_request': response_data,
            }

            utils._log_api_error(api_name="/v1/charging/requests/<int:request_id>/status", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Request lookup error: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    # ============================================
    # LISTING ENDPOINTS
    # ============================================

    @http.route('/v1/charging/requests/my-requests', type='http', auth='none', methods=['GET'], csrf=False)
    def list_my_requests(self, **kwargs):
        """List all charging requests for current user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            domain = [('request_user_id', '=', user.partner_id.id)]
            requests = request.env['request.charging'].with_user(user).search(domain, order="create_date desc")

            request_list = []
            for req in requests:
                request_list.append(req._get_prepared_charging_request_data())

            result = {
                'status': True,
                'charging_requests': request_list,
                'count': len(request_list)
            }

            utils._log_api_error(api_name="/v1/charging/requests/my-requests", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error listing charging requests: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/charging/requests/other-requests', type='http', auth='none', methods=['GET'], csrf=False)
    def list_other_requests(self, **kwargs):
        """List all charging requests for wallboxes owned by current user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            domain = [
                ('wallbox_owner_id', '=', user.partner_id.id),
                ('request_user_id', '!=', user.partner_id.id)
            ]
            requests = request.env['request.charging'].with_user(user).search(
                domain, 
                order="service_requested_date desc"
            )

            request_list = []
            for req in requests:
                request_list.append(req._get_prepared_charging_request_data())

            result = {
                'status': True,
                'charging_requests': request_list,
                'count': len(request_list)
            }

            utils._log_api_error(api_name="/v1/charging/requests/other-requests", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error listing other requests: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )
