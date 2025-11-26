# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class TripTrip(models.Model):
    _name = 'trip.trip'
    _description = 'Trip'

    vehicle_id = fields.Many2one('user.vehicle', string='Vehicle')
    vehicle_identifier = fields.Integer(string='Vehicle Identifier (legacy)')

    # Origin / Destination
    origin_latitude = fields.Float(string='Origin Latitude', digits=(12, 8))
    origin_longitude = fields.Float(string='Origin Longitude', digits=(12, 8))
    destination_latitude = fields.Float(string='Destination Latitude', digits=(12, 8))
    destination_longitude = fields.Float(string='Destination Longitude', digits=(12, 8))

    # Waypoints
    waypoint_ids = fields.One2many('trip.location', 'trip_id', string='Waypoints')

    distance = fields.Float(string='Distance (km)')
    duration = fields.Float(string='Duration (minutes)')
    date = fields.Datetime(string='Trip Date')

    pee = fields.Float(string='Equivalent Electrical Mileage (PEE)')

    # Savings
    saving_co2 = fields.Float(string='Saving CO2')
    saving_economics = fields.Float(string='Saving Economics')
    saving_tep = fields.Float(string='Saving TEP')

    # Suggested EVs
    advised_evehicle_ids = fields.One2many('trip.advised_evehicle', 'trip_id', string='Suggested e-vehicles')

    is_simulated = fields.Boolean(string='Is Simulated', default=False)
    is_electric = fields.Boolean(string='Is Electric')
    start_autonomy = fields.Float(string='Start Autonomy (km)')
