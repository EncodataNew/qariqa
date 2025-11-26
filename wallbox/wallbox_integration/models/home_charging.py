# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class WallboxCharging(models.Model):
    _name = 'wallbox.charging'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wallbox Charging Management'

    charge_id = fields.Char(string='Charge ID', required=True, readonly=True, copy=False, index=True)
    service_id = fields.Many2one('service.management', string='Service', required=True)
    reservation_requested = fields.Boolean(string='Reservation Requested')
    reservation_date = fields.Date(string='Reservation Date')
    service_requested_date = fields.Date(string='Service Requested Date')
    service_scheduled_date = fields.Date(string='Service Scheduled Date')
    service_completion_date = fields.Date(string='Service Completion Date')
    charging_duration = fields.Char(string='Charging Duration')

    service_cost = fields.Float(string='Service Cost')
    payment_method = fields.Selection([
        ('credit_card', 'Credit Card'),
        ('bank_transfer', 'Bank Transfer'),
    ], string='Payment Method')
    payment_status = fields.Selection([
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ], string='Payment Status')
    request_status = fields.Selection([
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ], string='Charging Status')

    customer_id = fields.Many2one('res.partner', string='Customer', required=True)
    wallbox_model_id = fields.Many2one('wallbox.model', string='Wallbox Model')
    building_id = fields.Many2one('building.management', string='Building')
    parking_space_id = fields.Many2one('parking.space', string='Parking Space')
    condominium_id = fields.Many2one('condominium.condominium', string='Condominium')

    charging_power = fields.Char(string='Charging Power')
    energy_consumed = fields.Char(string='Energy Consumed')

    documentation = fields.Text(string='Documentation')
    service_notes = fields.Text(string='Service Notes')
    customer_confirmation = fields.Boolean(string='Customer Confirmation')
