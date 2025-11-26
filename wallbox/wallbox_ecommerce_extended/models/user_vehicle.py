# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class UserVehicle(models.Model):
    _inherit = 'user.vehicle'

    request_charging_ids = fields.One2many('request.charging', 'vehicle_id', string='Charging Requests')
