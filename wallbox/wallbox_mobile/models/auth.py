# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.exceptions import UserError

class DeviceToken(models.Model):
    _name = 'wallbox.device.token'
    _description = 'Mobile Device Tokens for Push Notifications'

    user_id = fields.Many2one('res.users', required=True, ondelete='cascade')
    token = fields.Char('Device Token', required=True)
    platform = fields.Selection(
        [('expo', 'Expo'), ('ios', 'iOS'), ('android', 'Android')],
        string='Platform',
        default='expo'
    )
    active = fields.Boolean(default=True)
    message = fields.Char(string='Notification Message')

    def send_test_notification(self):
        if not self.message:
            raise UserError('Notification message is required.')
        notification_model = self.env['push.notification'].sudo()
        success = notification_model.send_expo_notification(self.user_id, self.message)

class IrConfigParameter(models.Model):
    _inherit = 'ir.config_parameter'

    @api.model
    def get_param(self, key, default=False):
        """Override to handle JWT secret initialization"""
        if key == 'jwt.secret':
            value = super().get_param(key)
            if not value:
                # Generate a new secret if none exists
                import secrets
                new_secret = secrets.token_urlsafe(64)
                self.sudo().set_param('jwt.secret', new_secret)
                return new_secret
            return value
        return super().get_param(key, default)
