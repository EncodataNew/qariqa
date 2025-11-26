# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields

class TripAdvisedEvehicle(models.Model):
    _name = 'trip.advised_evehicle'
    _description = 'Advised EV for a Trip'

    trip_id = fields.Many2one('trip.trip', string='Trip', ondelete='cascade')

    make = fields.Char(string='Make')
    model = fields.Char(string='Model')
    name = fields.Char(string='Name')

    autonomy = fields.Float(string='Autonomy (km)')
    mileage_perc = fields.Float(string='Mileage %')
    advise_perc = fields.Float(string='Advise %')
