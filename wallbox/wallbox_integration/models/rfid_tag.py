# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api


class RFIDTag(models.Model):
    _name = 'rfid.tag'
    _rec_name = 'tag_id'

    tag_id = fields.Char(string='Tag ID')
    is_allowed = fields.Boolean(string='Is Allowed')
    charging_station_id = fields.Many2one('charging.station', string='Charging Station ID')
