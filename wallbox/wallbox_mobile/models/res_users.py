# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api

class ResUsers(models.Model):
    _inherit = 'res.users'

    jwt_token = fields.Char("JWT token")
    device_token_ids = fields.One2many("wallbox.device.token", "user_id", string="Device Tokens")

    # def _check_credentials(self, password):
    #     try:
    #         return super(ResUsers, self)._check_credentials(password)
    #     except Exception as e:
    #         # Customize error messages for API
    #         if 'Invalid credentials' in str(e):
    #             raise Exception('Invalid email or password')
    #         raise
