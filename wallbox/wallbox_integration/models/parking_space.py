# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class ParkingSpace(models.Model):
    _name = 'parking.space'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Parking Space Management'

    # parking_space_id = fields.Char(string='Parking Space ID')
    name = fields.Char(string='Parking Lot Name/Number')
    building_id = fields.Many2one('building.building', string="Building", required=True)
    condominium_id = fields.Many2one('condominium.condominium', string="Condominium", required=True)
    parking_type = fields.Selection([
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('underground', 'Underground')
    ], string='Type')
    total_area = fields.Float(string='Total Area (sqm)')
    capacity = fields.Integer(string='Capacity (Number of Vehicles)')
    assigned_or_shared = fields.Selection([
        ('assigned', 'Assigned'),
        ('shared', 'Shared')
    ], string='Assigned or Shared')
    # owner_id = fields.Many2one('res.partner', string="Owner", domain=[('is_wallbox_user','=', True)])

    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        domain=lambda self: self._get_filtered_customer_domain()
    )

    @api.model
    def _get_filtered_customer_domain(self):
        domain = []
        # domain = [('is_wallbox_user', '=', True)]
        user_partner_id = self.env.user.partner_id.id

        if self.env.user.has_group('wallbox_integration.group_wallbox_admin'):
            return domain
        elif self.env.user.has_group('wallbox_integration.group_wallbox_user'):
            return domain + [('id', '=', user_partner_id)]
        return [('id', '=', -1)]

    rental_status = fields.Selection([
        ('owned', 'Owned'),
        ('rented', 'Rented')
    ], string='Rental Status')
    monthly_fee = fields.Float(string='Monthly Fee (if rented)') #TODO : hide this field if rental_status is owned
    # related_condominium_id = fields.Many2one('condominium.condominium', string="Related Condominium", ondelete='set null')
    # related_building_id = fields.Many2one('building.building', string="Related Building", ondelete='set null')
    access_control_system = fields.Boolean(string='Access Control System')
    ev_charging_station = fields.Boolean(string='EV Charging Station Available')
    handicap_accessibility = fields.Boolean(string='Handicap Accessibility')
    maintenance_records = fields.Text(string='Maintenance Records')
    last_inspection_date = fields.Date(string='Last Inspection Date')

    charging_station_ids = fields.One2many('charging.station', 'parking_space_id', string='Charging Stations')

    number_of_charging_stations = fields.Integer(
        string='Number of Charging Stations',
        compute='_compute_charging_station_count',
        store=True
    )

    @api.depends('charging_station_ids')
    def _compute_charging_station_count(self):
        for record in self:
            record.number_of_charging_stations = len(record.charging_station_ids)

    def action_view_charging_stations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Charging Stations',
            'res_model': 'charging.station',
            'view_mode': 'list,form',
            'domain': [('parking_space_id', '=', self.id)],
            'context': {
                'default_parking_space_id': self.id,
                'default_building_id': self.building_id.id,
                'default_condominium_id': self.condominium_id.id
            }
        }

    @api.onchange('rental_status')
    def _onchange_rental_status(self):
        """Hide monthly fee when status is owned"""
        if self.rental_status == 'owned':
            self.monthly_fee = 0.0

    number_of_users = fields.Integer(
        string='Number of Users',
        compute='_compute_number_of_users',
        store=True
    )
    wallbox_user_ids = fields.One2many('res.partner', 'parking_space_id', string='Wallbox Users')

    @api.depends('wallbox_user_ids')
    def _compute_number_of_users(self):
        for record in self:
            record.number_of_users = len(record.wallbox_user_ids)

    # def action_view_wallbox_users(self):
    #     self.ensure_one()
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'name': 'Wallbox Users',
    #         'res_model': 'res.partner',
    #         'view_mode': 'list,form',
    #         'domain': [('parking_space_id', '=', self.id)],
    #         'context': {'default_parking_space_id': self.id}
    #     }
