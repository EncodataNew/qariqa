# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class BuildingCondominium(models.Model):
    _name = 'building.building'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Building Condominium'
    _rec_name = 'building_name'

    # identification_code = fields.Char(string='Identification Code', required=True)
    # condominium_code = fields.Char(string='Condominium Code', required=True)
    building_name = fields.Char(string='Name', help="Building name or Code")
    address = fields.Text(string='Address')
    gps_coordinates = fields.Char(string='GPS Coordinates')
    year_of_construction = fields.Integer(string='Year of Construction')
    total_area = fields.Float(string='Total Area')
    number_of_floors = fields.Integer(string='Number of Floors')
    # owner_id = fields.Many2one('res.partner', string='Owner', domain=[('is_condominium_owner','=', True)])
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        domain=lambda self: self._get_filtered_customer_domain()
    )

    number_of_users = fields.Integer(
        string='Number of Users',
        compute='_compute_number_of_users',
        store=True
    )
    wallbox_user_ids = fields.One2many('res.partner', 'building_id', string='Wallbox Users')

    @api.depends('wallbox_user_ids')
    def _compute_number_of_users(self):
        for record in self:
            record.number_of_users = len(record.wallbox_user_ids)

    @api.model
    def _get_filtered_customer_domain(self):
        domain = [('is_condominium_owner', '=', True)]
        user_partner_id = self.env.user.partner_id.id

        if self.env.user.has_group('wallbox_integration.group_wallbox_admin'):
            return domain
        elif self.env.user.has_group('wallbox_integration.group_wallbox_user'):
            return domain + [('id', '=', user_partner_id)]
        return [('id', '=', -1)]


    manager_id = fields.Many2one('res.partner', string='Manager/Maintenance Provider', required=True, domain=[('is_condominium_owner','=', True)])
    type_of_ownership = fields.Selection([
        ('private', 'Private'),
        ('public', 'Public'),
        ('mixed', 'Mixed')
    ], string='Type of Ownership')

    intended_use = fields.Char(string='Intended Use')
    main_construction_materials = fields.Char(string='Main Construction Materials')
    energy_class = fields.Char(string='Energy Class')
    heating_cooling_system = fields.Char(string='Heating and Cooling System')
    installed_systems = fields.Text(string='Installed Systems')
    number_of_real_estate_units = fields.Integer(string='Number of Real Estate Units')

    blueprints = fields.Binary(string='Blueprints and Architectural Plans')
    energy_certifications = fields.Binary(string='Energy Certifications')
    building_permits = fields.Binary(string='Building Permits and Authorizations')
    insurance_policies = fields.Binary(string='Building Insurance Policies')
    maintenance_contracts = fields.Binary(string='Maintenance and Management Contracts')

    compliance_certificates = fields.Binary(string='Compliance Certificates')
    evacuation_safety_plan = fields.Binary(string='Evacuation and Safety Plan')
    fire_prevention_systems = fields.Text(string='Fire Prevention Systems')
    accessibility_features = fields.Text(string='Accessibility for People with Disabilities')

    recent_renovation_work = fields.Text(string='Recent Renovation Work')
    routine_maintenance = fields.Text(string='Routine and Extraordinary Maintenance Interventions')
    reported_issues = fields.Text(string='Reported Issues and Malfunctions')

    condominium_id = fields.Many2one('condominium.condominium', string='Condominium', required=True)
    parking_space_ids = fields.One2many('parking.space', 'building_id', string='Parking Space')
    charging_station_ids = fields.One2many('charging.station', 'building_id', string='Charging Station')

    number_of_parking_spaces = fields.Integer(
        string='Number of Parking Spaces',
        compute='_compute_parking_space_count',
        store=True
    )
    number_of_charging_stations = fields.Integer(
        string='Number of Charging Stations',
        compute='_compute_charging_station_count',
        store=True
    )

    @api.depends('parking_space_ids')
    def _compute_parking_space_count(self):
        for record in self:
            record.number_of_parking_spaces = len(record.parking_space_ids)

    @api.depends('charging_station_ids')
    def _compute_charging_station_count(self):
        for record in self:
            record.number_of_charging_stations = len(record.charging_station_ids)

    def action_view_parking_spaces(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Parking Spaces',
            'res_model': 'parking.space',
            'view_mode': 'list,form',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id}
        }

    def action_view_wallbox_users(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wallbox Users',
            'res_model': 'res.partner',
            'view_mode': 'list,form',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id}
        }

    def action_view_charging_stations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Charging Stations',
            'res_model': 'charging.station',
            'view_mode': 'list,form',
            'domain': [('building_id', '=', self.id)],
            'context': {'default_building_id': self.id}
        }
