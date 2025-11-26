# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class TripLocation(models.Model):
    _name = 'trip.location'
    _description = 'Trip Waypoint Location'

    trip_id = fields.Many2one('trip.trip', string='Trip', ondelete='cascade')
    latitude = fields.Float(string='Latitude', digits=(12, 8))
    longitude = fields.Float(string='Longitude', digits=(12, 8))
