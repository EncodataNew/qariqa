# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class ServiceManagement(models.Model):
    _name = 'service.management'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Service Management'

    name = fields.Char(string='Service Name', required=True)
    service_category = fields.Selection([
        ('regular', 'Regular Charging'),
        ('fast', 'Fast Charging')
    ], string='Service Category')
    service_info = fields.Text(string='Service Info')
    reservation_required = fields.Boolean(string='Reservation Required')
    cost_per_session = fields.Float(string='Cost Per Session')
    payment_method = fields.Selection([
        ('credit_card', 'Credit Card'),
        ('app', 'App'),
    ], string='Payment Method')
    user_type = fields.Selection([
        ('fixed', 'Fixed Customers'),
        ('guest', 'Guests'),
        ('both', 'Both')
    ], string='User Type')
    service_duration = fields.Char(string='Service Duration')
    location = fields.Char(string='Location')
    wallbox_type = fields.Selection([
        ('standard', 'Standard'),
        ('fast', 'Fast')
    ], string='Wallbox Type')
    charging_power = fields.Float(string='Charging Power')
    documentation = fields.Text(string='Documentation')
    service_notes = fields.Text(string='Service Notes')
    maintenance_schedule = fields.Text(string='Maintenance Schedule')
    intervention_history = fields.Text(string='Intervention History')
