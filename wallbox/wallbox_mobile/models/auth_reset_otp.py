# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import secrets
import hashlib
from datetime import timedelta

from odoo import api, fields, models, _


class PasswordResetOTP(models.Model):
    _name = 'auth.reset.otp'
    _description = 'Password Reset OTP Store'
    _rec_name = 'user_id'
    _order = 'create_date desc'

    user_id = fields.Many2one('res.users', required=True, index=True, ondelete='cascade')
    email = fields.Char(required=True, index=True)

    # OTP fields
    otp_hash = fields.Char(index=True)
    otp_salt = fields.Char()
    otp_expires_at = fields.Datetime()
    otp_attempts = fields.Integer(default=0)

    # Resend/rate-limit fields
    resend_count = fields.Integer(default=0)
    last_sent_at = fields.Datetime()

    # Reset token (after OTP verification)
    reset_token = fields.Char(index=True)
    reset_token_expires_at = fields.Datetime()

    # Flags
    used = fields.Boolean(default=False)
    active = fields.Boolean(default=True)

    # -------------------- helpers --------------------
    @api.model
    def _hash_value(self, value: str, salt: str = None):
        if not salt:
            salt = secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac(
            'sha256', value.encode('utf-8'), salt.encode('utf-8'), 120000
        )
        return digest.hex(), salt

    def set_otp(self, otp: str, validity_seconds: int = 120):
        h, s = self._hash_value(otp)
        self.write({
            'otp_hash': h,
            'otp_salt': s,
            'otp_expires_at': fields.Datetime.now() + timedelta(seconds=validity_seconds),
            'otp_attempts': 0,
            'resend_count': (self.resend_count or 0) + 1,
            'last_sent_at': fields.Datetime.now(),
            'reset_token': False,
            'reset_token_expires_at': False,
            'used': False,
        })

    def check_otp(self, otp: str):
        if not self.otp_hash or not self.otp_salt or not self.otp_expires_at:
            return False, 'OTP not set'
        if fields.Datetime.now() > self.otp_expires_at:
            return False, 'OTP expired'
        # Count attempt
        self.write({'otp_attempts': (self.otp_attempts or 0) + 1})
        digest, _ = self._hash_value(otp, self.otp_salt)
        if secrets.compare_digest(digest, self.otp_hash):
            return True, None
        return False, 'Invalid OTP'

    def issue_reset_token(self, validity_seconds: int = 300) -> str:
        token = secrets.token_urlsafe(32)
        self.write({
            'reset_token': token,
            'reset_token_expires_at': fields.Datetime.now() + timedelta(seconds=validity_seconds),
        })
        return token
