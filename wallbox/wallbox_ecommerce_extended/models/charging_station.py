# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ChargingStation(models.Model):
    _inherit = 'charging.station'

    serial_number = fields.Char(string='Serial Number', readonly=True)
    invitation_ids = fields.One2many('charging.station.invitation', 'charging_station_id', string='Invitations')

    # call sync method for manully update charger to CSMS server
    def sync_with_csms(self):
        if not self.price_per_kwh:
            raise ValidationError(_('Price Per KWH is not set.'))
        if not self.guest_max_amount_limit:
            raise ValidationError(_('Guest max amount limit is not set.'))
        cms_api = self.env['csms.api'].sudo()
        cms_api.sync_charger_status(self)

    def reset_charger(self):
        cms_api = self.env['csms.api'].sudo()
        if self.charger_id:
            cms_api.reset_charger(charger_id=self.charger_id)

    # Update the charger record in CSMS server when following fields is changed in odoo
    # price_per_kwh, subscription_exp_date, latitude, longitude
    def write(self, vals):
        # First call the original write method
        res = super(ChargingStation, self).write(vals)

        # Fields that should trigger sync with CSMS when changed
        sync_fields = ['price_per_kwh', 'subscription_exp_date', 'latitude', 'longitude', 'rfid_tag_ids']
        # Check if any of the tracked fields were modified
        if any(field in vals for field in sync_fields):
            for record in self:
                record.sync_with_csms()
        return res

    def action_view_charging_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Charging Requests',
            'res_model': 'request.charging',
            'view_mode': 'list,form',
            'domain': [('charging_station_id', '=', self.id)],
        }

    def action_view_invitations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Invitations',
            'res_model': 'charging.station.invitation',
            'view_mode': 'list,form',
            'domain': [('charging_station_id', '=', self.id)],
            'context': {'default_charging_station_id': self.id}
        }
