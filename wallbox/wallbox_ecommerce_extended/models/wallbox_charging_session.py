# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from datetime import datetime


class WallboxChargingSession(models.Model):
    _inherit = 'wallbox.charging.session'

    request_id = fields.Many2one('request.charging', string='Request Ref')
