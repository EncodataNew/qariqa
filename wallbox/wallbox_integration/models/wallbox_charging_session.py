# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime


class WallboxChargingSession(models.Model):
    _name = 'wallbox.charging.session'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wallbox Charging Session'
    _rec_name = 'transaction_id'
    _order = 'id desc'

    # name = fields.Char(string='Session Number', required=True, default="New")
    transaction_id = fields.Char(string="Transaction ID", required=True, help='Id Comes from wallbox api response when session is created on CSMS.', tracking=True)
    charging_station_id = fields.Many2one('charging.station', string="Charging Station", required=True, tracking=True)
    customer_id = fields.Many2one('res.partner', string="Customer", required=True, tracking=True)
    max_amount_limit = fields.Float(string='Max Amount Limit', tracking=True)

    start_meter = fields.Float(string="Meter Start Value (Wh)", tracking=True)
    stop_meter = fields.Float(string="Meter Stop Value (Wh)", tracking=True)
    total_energy = fields.Float(string='Total Energy (Wh)', tracking=True)
    cost = fields.Float(string="Cost", readonly=True, tracking=True)
    status = fields.Selection([
        ('Started', 'Started'),
        ('Ended', 'Ended'),
        ('Failed', 'Failed')
    ], string="Status", tracking=True)

    created_at = fields.Datetime(string='Created in CSMS', tracking=True)
    updated_at = fields.Datetime(string='Updated in CSMS', tracking=True)
    vehicle_id = fields.Many2one('user.vehicle', string='Vehicle', tracking=True)

    start_time = fields.Datetime(string="Start Time", readonly=True, tracking=True)
    end_time = fields.Datetime(string="End Time", readonly=True, tracking=True)
    total_duration = fields.Char(string="Total Duration", readonly=True, tracking=True)
        
    def view_charging_session(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wallbox Charging Session',
            'res_model': 'wallbox.charging.session',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'current',
        }

    def action_view_related_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Logs for {self.transaction_id}',
            'res_model': 'wallbox.log',
            'view_mode': 'list,form',
            'domain': [
                ('charger_id', '=', self.charging_station_id.charger_id),
                ('created_at', '>=', self.start_time),
                ('created_at', '<=', self.end_time)
            ]
        }
