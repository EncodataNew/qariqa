# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class UserVehicle(models.Model):
    _name = 'user.vehicle'
    _description = 'User Vehicles'

    name = fields.Char(string="Vehicle Name", required=True)
    brand = fields.Char(string='Brand', required=True)
    model = fields.Char(string='Model', required=True)
    licence_plate = fields.Char(string='Licence Plate', required=True)
    charging_power = fields.Float(string='Charging Power (kW)')
    connector_type = fields.Selection([
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('ccs', 'CCS'),
        ('chademo', 'CHAdeMO'),
    ], string='Connector Type')

    emissions = fields.Char(string='Emissions')
    consumption = fields.Char(string='Consumption')
    autonomy = fields.Char(string='Autonomy')
    battery_capacity = fields.Char(string='Battery Capacity')
    vehicle_type = fields.Selection([
        ('A0', 'A0'),
        ('B0', 'B0'),
        ('B1', 'B1'),
        ('B2', 'B2'),
        ('C0', 'C0'),
        ('C1', 'C1'),
        ('C2', 'C2'),
        ('D0', 'D0'),
        ('D1', 'D1'),
        ('D2', 'D2'),
        ('E0', 'E0'),
        ('E1', 'E1'),
        ('E2', 'E2'),
        ('F0', 'F0'),
        ('F2', 'F2'),
        ('J2', 'J2'),
        ('S0', 'S0'),
        ('S2', 'S2'),
        ('Z0', 'Z0'),
        ('minivan', 'Minivan'),
        ('van', 'Van'),
        ('truck', 'Truck'),
    ], string='Vehicle Type')

    fuel_type = fields.Selection([
        ('Gas', 'gas'),
        ('Diesel', 'diesel'),
        ('GPL', 'natural-gas-cng'),
        ('METHANE', 'Flex-fuel-ffv'),
        ('Electric', 'electric')
    ], string='Fuel Type')
    is_default = fields.Boolean(string='Is Default', help="Set as default vehicle")

    partner_id = fields.Many2one('res.partner', string='Customer', required=True, readonly=True, 
        default=lambda self: self.env.user.partner_id.id)

    _sql_constraints = [
        ('licence_plate_partner_id_uniq', 'unique (licence_plate, partner_id)', "Licence plate already exists for this customer!"),
    ]
