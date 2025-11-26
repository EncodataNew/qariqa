# -*- coding: utf-8 -*-
import json
import logging
import secrets
from datetime import timedelta

from odoo import http, _, SUPERUSER_ID, fields
from odoo.http import request, Response
from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)

try:
    # Reuse your existing utils for consistent API responses
    from odoo.addons.wallbox_mobile import utils
except Exception:  # fallback if utils not available in testing
    class utils:
        @staticmethod
        def _error_response(code, message):
            return {"status": False, "error": {"code": code, "message": str(message)}}
        @staticmethod
        def _success_response(data=None):
            data = data or {}
            data.setdefault('status', True)
            return data


class PasswordResetController(http.Controller):

    # Small JSON helper (only used by /me-like endpoints). Not strictly required here.
    def _json(self, data, status=200):
        return Response(json.dumps(data), status=status, mimetype='application/json')

    # ---------------- 1) Request OTP ----------------
    @http.route('/v1/auth/password/request-otp', type='json', auth='none', methods=['POST'], csrf=False)
    def request_otp(self, **kwargs):
        ensure_db()
        try:
            payload = json.loads(request.httprequest.data or '{}')
            email = (payload.get('email') or '').strip().lower()
            if not email:
                return utils._error_response('VALIDATION_ERROR', _('Email is required'))

            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            # Privacy-friendly response: do not reveal if user/email exists
            if not user or not user.exists() or not user.email:
                return utils._success_response({'message': _('If an account exists, an OTP has been sent')})

            Reset = request.env['auth.reset.otp'].sudo()
            rec = Reset.search([('user_id', '=', user.id), ('active', '=', True)], limit=1)
            if not rec:
                rec = Reset.create({'user_id': user.id, 'email': email})
            # Basic rate limit
            if rec.last_sent_at and (fields.Datetime.now() - rec.last_sent_at).total_seconds() < 30:
                return utils._error_response('RATE_LIMITED', _('Please wait a few seconds before requesting a new OTP'))
            if rec.resend_count and rec.resend_count >= 5 and rec.last_sent_at and (fields.Datetime.now() - rec.last_sent_at).total_seconds() < 3600:
                return utils._error_response('RATE_LIMITED', _('Too many OTP requests. Try again later.'))

            # Generate a 6-digit numeric OTP
            otp = f"{secrets.randbelow(1_000_000):06d}"
            rec.set_otp(otp, validity_seconds=120)

            # Send Mail (template preferred; fallback to plain mail)
            try:
                email_template = request.env.ref('wallbox_mobile.mail_template_password_reset_otp', raise_if_not_found=False).sudo()
                if email_template:
                    template = email_template.with_context(otp=otp, user_name=user.name)
                    email_values = {
                        'email_to': user.email,
                        'email_cc': False,
                        'auto_delete': True,
                        'recipient_ids': [],
                        'partner_ids': [],
                        'scheduled_date': False,
                    }
                    # with request.env.cr.savepoint():
                    template.send_mail(user.id, force_send=True, email_values=email_values, email_layout_xmlid='mail.mail_notification_light')
                else:
                    mail_vals = {
                        'subject': _('Your password reset code: %s') % otp,
                        'body_html': _('<p>Hello %s,</p><p>Your password reset code is <b>%s</b>. It will expire in 2 minutes.</p>') % (user.name or '', otp),
                        'email_to': user.email,
                    }
                    request.env['mail.mail'].sudo().create(mail_vals).send()
                utils._log_api_error(api_name="/v1/auth/password/request-otp", error_code="SUCCESS", error_description="No Error", json_parameters=None, user=user)
            except Exception as e:
                _logger.warning('Failed to send OTP email: %s', e)
                return utils._error_response('EMAIL_FAILED', _('Failed to send OTP. Please try again.'))

            return utils._success_response({'message': _('OTP sent to your email')})

        except Exception as e:
            _logger.exception('request_otp error: %s', e)
            return utils._error_response('INTERNAL_ERROR', _('Could not process OTP request'))

    # ---------------- 2) Verify OTP ----------------
    @http.route('/v1/auth/password/verify-otp', type='json', auth='none', methods=['POST'], csrf=False)
    def verify_otp(self, **kwargs):
        ensure_db()
        try:
            payload = json.loads(request.httprequest.data or '{}')
            email = (payload.get('email') or '').strip().lower()
            otp = (payload.get('otp') or '').strip()

            if not email or not otp:
                return utils._error_response('VALIDATION_ERROR', _('Email and OTP are required'))

            user = request.env['res.users'].sudo().search([('login', '=', email)], limit=1)
            if not user or not user.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', _('Invalid OTP or email'))

            rec = request.env['auth.reset.otp'].sudo().search([('user_id', '=', user.id), ('active', '=', True)], limit=1)
            if not rec:
                return utils._error_response('OTP_INVALID', _('Please request a new OTP'))

            # limit attempts
            if (rec.otp_attempts or 0) >= 5:
                return utils._error_response('OTP_TOO_MANY_ATTEMPTS', _('Too many incorrect attempts. Request a new OTP.'))

            ok, err = rec.check_otp(otp)
            if not ok:
                return utils._error_response('OTP_INVALID', err or _('Invalid OTP'))

            # Short-lived reset token (5 minutes)
            token = rec.issue_reset_token(validity_seconds=300)

            result = {'reset_token': token, 'expires_in': 300}

            utils._log_api_error(api_name="/v1/auth/password/verify-otp", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return utils._success_response(result)

        except Exception as e:
            _logger.exception('verify_otp error: %s', e)
            return utils._error_response('INTERNAL_ERROR', _('Could not verify OTP'))

    # ------------- 3) Reset with reset_token -------------
    @http.route('/v1/auth/password/reset', type='json', auth='none', methods=['POST'], csrf=False)
    def reset_password(self, **kwargs):
        ensure_db()
        try:
            payload = json.loads(request.httprequest.data or '{}')
            reset_token = (payload.get('reset_token') or '').strip()
            new_password = (payload.get('new_password') or '').strip()
            confirm_password = (payload.get('confirm_password') or '').strip()

            if not reset_token or not new_password or not confirm_password:
                return utils._error_response('VALIDATION_ERROR', _('reset_token, new_password and confirm_password are required'))
            if new_password != confirm_password:
                return utils._error_response('VALIDATION_ERROR', _('Passwords do not match'))
            if len(new_password) < 8:
                return utils._error_response('WEAK_PASSWORD', _('Password must be at least 8 characters'))

            rec = request.env['auth.reset.otp'].sudo().search([
                ('reset_token', '=', reset_token), ('active', '=', True), ('used', '=', False)
            ], limit=1)
            if not rec or not rec.user_id:
                return utils._error_response('TOKEN_INVALID', _('Invalid or used reset token'))

            if not rec.reset_token_expires_at or fields.Datetime.now() > rec.reset_token_expires_at:
                return utils._error_response('TOKEN_EXPIRED', _('Reset token expired'))

            try:
                rec.user_id.sudo().write({'password': new_password})
            except Exception as e:
                _logger.error('Failed to update password: %s', e)
                return utils._error_response('INTERNAL_ERROR', _('Failed to update password'))

            rec.write({'used': True, 'active': False, 'reset_token': False, 'otp_hash': False, 'otp_salt': False})

            # Send Notification on mobile app of registrade user.
            notification_model = request.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(rec.user_id, 'Password changed successfully.')

            result = {'message': _('Password changed successfully')}

            utils._log_api_error(api_name="/v1/auth/password/reset", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=None)

            return utils._success_response(result)

        except Exception as e:
            _logger.exception('reset_password error: %s', e)
            return utils._error_response('INTERNAL_ERROR', _('Could not reset password'))
