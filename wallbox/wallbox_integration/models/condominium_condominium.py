# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class CondominiumManagement(models.Model):
    _name = 'condominium.condominium'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Condominium Management'
    _rec_name = 'condominium_name'

    condominium_name = fields.Char(string='Name', required=True)
    address = fields.Text(string='Address')
    number_of_buildings = fields.Integer(
        string='Number of Buildings',
        compute='_compute_building_count',
        store=True
    )
    number_of_parking_spaces = fields.Integer(
        string='Number of Parking Spaces',
        compute='_compute_parking_space_count',
        store=True
    )
    number_of_users = fields.Integer(
        string='Number of Users',
        compute='_compute_number_of_users',
        store=True
    )
    number_of_residential_units = fields.Integer(string='Number of Residential Units')
    number_of_commercial_units = fields.Integer(string='Number of Commercial Units')
    total_number_of_occupants = fields.Integer(string='Total Number of Occupants')
    common_property_percentage_per_unit = fields.Float(string='Common Property Percentage Per Unit')
    manager_id = fields.Many2one('res.partner', string='Condominium Manager', 
        domain=lambda self: self._get_filtered_customer_domain())
    owner_id = fields.Many2one('res.partner', string='Owner',
        required=True, domain=lambda self: self._get_filtered_customer_domain())

    @api.model
    def _get_filtered_customer_domain(self):
        domain = [('is_condominium_owner', '=', True)]
        user_partner_id = self.env.user.partner_id.id

        if self.env.user.has_group('wallbox_integration.group_wallbox_admin'):
            return domain
        elif self.env.user.has_group('wallbox_integration.group_wallbox_condo_owner'):
            return domain + [('id', '=', user_partner_id)]
        return [('id', '=', -1)]

    type_of_condominium = fields.Selection([
        ('residential', 'Residential'),
        ('mixed-use', 'Mixed-Use'),
        ('office', 'Office')
    ], string='Type of Condominium')

    annual_condominium_fees = fields.Float(string='Annual Condominium Fees')
    common_areas = fields.Text(string='Common Areas (gardens, parking, amenities)')
    elevator_count = fields.Integer(string='Elevator Count')
    waste_management_system = fields.Text(string='Waste Management System')
    heating_system = fields.Selection([
        ('centralized', 'Centralized'),
        ('independent', 'Independent')
    ], string='Heating System')
    security_systems = fields.Text(string='Security Systems (surveillance, access control)')
    fire_prevention_systems = fields.Text(string='Fire Prevention Systems')

    insurance_coverage = fields.Binary(string='Insurance Coverage for Common Areas')
    condominium_regulations = fields.Binary(string='Condominium Regulations')
    meeting_minutes = fields.Binary(string='Meeting Minutes of Condominium Assemblies')
    maintenance_contracts = fields.Binary(string='Maintenance Contracts for Common Areas')
    legal_disputes = fields.Text(string='Legal Disputes (if any)')

    safety_inspections = fields.Binary(string='Safety Inspections and Certifications')
    accessibility_features = fields.Text(string='Accessibility Features (ramps, elevators, etc.)')
    scheduled_maintenance_plans = fields.Text(string='Scheduled Maintenance Plans')
    last_extraordinary_maintenance = fields.Text(string='Last Extraordinary Maintenance Interventions')
    ongoing_issues = fields.Text(string='Ongoing Issues and Complaints')

    # relational fields
    building_ids = fields.One2many('building.building', 'condominium_id', string="Buildings")
    parking_space_ids = fields.One2many('parking.space', 'condominium_id', string='Parking Space')
    wallbox_user_ids = fields.One2many('res.partner', 'condominium_id', string='Wallbox Users')

    @api.depends('building_ids')
    def _compute_building_count(self):
        for record in self:
            record.number_of_buildings = len(record.building_ids)

    @api.depends('wallbox_user_ids')
    def _compute_number_of_users(self):
        for record in self:
            record.number_of_users = len(record.wallbox_user_ids)

    @api.depends('parking_space_ids')
    def _compute_parking_space_count(self):
        for record in self:
            record.number_of_parking_spaces = len(record.parking_space_ids)

    def action_view_buildings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Buildings',
            'res_model': 'building.building',
            'view_mode': 'list,form',
            'domain': [('condominium_id', '=', self.id)],
            'context': {'default_condominium_id': self.id}
        }

    def action_view_wallbox_users(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wallbox Users',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('condominium_id', '=', self.id)],
            'context': {'default_condominium_id': self.id}
        }

    def action_view_parking_spaces(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parking Spaces',
            'res_model': 'parking.space',
            'view_mode': 'list,form',
            'domain': [('condominium_id', '=', self.id)],
            'context': {'default_condominium_id': self.id}
        }
