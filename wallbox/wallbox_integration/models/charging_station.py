# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError


class ChargingStation(models.Model):
    _name = 'charging.station'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'EV Charging Station'

    name = fields.Char(string='Charging Station Name/Code', help="Charging Station Name/Code")
    wallbox_order_id = fields.Many2one('wallbox.order', string='Wallbox Order', readonly=True)

    # Property Fields
    condominium_id = fields.Many2one('condominium.condominium', string='Condominium', related="wallbox_order_id.condominium_id") 
    building_id = fields.Many2one('building.building', string='Building', related="wallbox_order_id.building_id")
    parking_space_id = fields.Many2one('parking.space', string='Parking Space', related="wallbox_order_id.parking_space_id")

    installation_date = fields.Date(string='Installation Date', required=True)
    location = fields.Selection([
        ('indoor', 'Indoor'),
        ('outdoor', 'Outdoor'),
        ('underground', 'Underground')
    ], string='Location', tracking=True)
    charging_power = fields.Float(string='Charging Power (kW)')
    guest_max_amount_limit = fields.Float(string='Guest Max Amount Limit', tracking=True,
        help="this amount is used for block amount in customers account for guest scenario.")
    connector_type = fields.Selection([
        ('type2', 'Type 2'),
        ('chademo', 'CHAdeMO'),
        ('ccs', 'CCS')
    ], string='Connector Type')
    number_of_ports = fields.Integer(string='Number of Charging Ports', default=1, readonly=True)
    access_type = fields.Selection([
        ('private', 'Private'),
        ('public', 'Public'),
        ('condominium', 'Condominium')
    ], string='Access Type')
    authentication_method = fields.Selection([
        ('rfid', 'RFID'),
        ('app', 'App'),
        ('free', 'Free Access')
    ], string='Authentication Method')
    energy_source = fields.Selection([
        ('grid', 'Grid'),
        ('solar', 'Solar'),
        ('mixed', 'Mixed')
    ], string='Energy Source')
    billing_system = fields.Selection([
        ('flat_rate', 'Flat Rate'),
        ('pay_per_use', 'Pay-per-Use'),
        ('free', 'Free')
    ], string='Billing System')
    last_maintenance_date = fields.Date(string='Last Maintenance Date')
    next_scheduled_maintenance = fields.Date(string='Next Scheduled Maintenance')
    reported_issues = fields.Text(string='Reported Issues')

    charging_session_ids = fields.One2many('wallbox.charging.session', 'charging_station_id', string='Charging Sessions')
    wallbox_log_ids = fields.One2many('wallbox.log', 'charging_station_id', string="Wallbox Logs")

    number_of_charging_sessions = fields.Integer(
        string='Number of Charging Sessions',
        compute='_compute_charging_session_count',
        store=True
    )

    # CMS server fields
    # odoo_id = consider as standard model id
    charger_id = fields.Char(string='Charger ID', required=True, readonly=True, related="wallbox_order_id.installation_id.charger_id")
    owner_id = fields.Many2one('res.partner', string='Owner/Administrator', related="wallbox_order_id.customer_id")
    status = fields.Selection(
        selection=[
            ('Available', 'Available'),
            ('Preparing', 'Preparing'),
            ('Charging', 'Charging'),
            ('SuspendedEVSE', 'SuspendedEVSE'),
            ('SuspendedEV', 'SuspendedEV'),
            ('Finishing', 'Finishing'),
            ('Reserved', 'Reserved'),
            ('Unavailable', 'Unavailable'),
            ('Faulted', 'Faulted'),
        ], string='status', tracking=True)
    price_per_kwh = fields.Float(string='Price Per KW', tracking=True)
    # created_at = fields.Datetime(string='Created At')
    # updated_at = fields.Datetime(string='Updated At')
    latitude = fields.Float(string="Latitude", digits=(10, 7), aggregator=None, tracking=True)
    longitude = fields.Float(string="Longitude", digits=(10, 7), aggregator=None, tracking=True)
    ws_url = fields.Char(string='WS URL', readonly=True)

    allowed_partner_ids = fields.Many2many(
        'res.partner',
        'charging_station_partner_rel',
        'charging_station_id',
        'partner_id',
        string='Allowed users for monthly billing',
        help='Partners associated with this charging station'
    )
    rfid_tag_ids = fields.One2many('rfid.tag', 'charging_station_id', string='RFID Tags')
    total_energy = fields.Float(compute='_compute_total_energy', string='Total Energy', store=True)
    total_recharged_cost = fields.Float(compute='_compute_total_recharged_cost', string='Total Recharged Cost', store=True)

    @api.depends('charging_session_ids')
    def _compute_charging_session_count(self):
        for record in self:
            record.number_of_charging_sessions = len(record.charging_session_ids)

    @api.depends('charging_session_ids', 'charging_session_ids.total_energy')
    def _compute_total_energy(self):
        for station in self:
            if station.charging_session_ids:
                station.total_energy = sum(station.charging_session_ids.mapped('total_energy'))

    @api.depends('charging_session_ids', 'charging_session_ids.cost')
    def _compute_total_recharged_cost(self):
        for station in self:
            if station.charging_session_ids:
                station.total_recharged_cost = sum(station.charging_session_ids.mapped('cost'))

    def action_view_charging_sessions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Charging Sessions',
            'res_model': 'wallbox.charging.session',
            'view_mode': 'list,form',
            'domain': [('charging_station_id', '=', self.id)],
            'context': {
                'default_charging_station_id': self.id,
                'default_building_id': self.building_id.id,
                'default_parking_space_id': self.parking_space_id.id
            }
        }

    def action_view_charging_station_logs(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Wallbox Logs',
            'res_model': 'wallbox.log',
            'view_mode': 'list,form',
            'domain': [('charging_station_id', '=', self.id)],
        }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('charging.station') or _('New')
        return super().create(vals_list)
