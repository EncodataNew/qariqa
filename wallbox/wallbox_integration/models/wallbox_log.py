# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)

class WallboxLog(models.Model):
    _name = 'wallbox.log'
    _description = 'Wallbox API Logs'
    _order = "create_date desc"
    _rec_name = 'charger_id'

    message = fields.Text(string="Message", required=True)
    payload = fields.Text(string="Payload", required=True)
    charger_id = fields.Char(string='Charger ID', required=True)
    direction = fields.Selection([
        ('C2S', 'C2S'),
        ('S2C', 'S2C'),
    ], string="Direction", required=True)
    created_at = fields.Datetime(string='Created at')
    updated_at = fields.Datetime(string='Updated at')
    not_necessary = fields.Boolean(string='Not Necessary')
    charging_station_id = fields.Many2one('charging.station', string='Charging Station')

    @api.model
    def _delete_unnecessary_logs(self, limit=1000):
        """Delete logs marked as not necessary with safety limit"""
        try:
            unnecessary_logs = self.sudo().search([('not_necessary', '=', True)], limit=limit)
            if unnecessary_logs:
                count = len(unnecessary_logs)
                unnecessary_logs.sudo().unlink()
                _logger.info(f"Deleted {count} unnecessary wallbox logs (limit: {limit})")
                return count
            return 0
        except Exception as e:
            _logger.error(f"Failed to delete unnecessary wallbox logs: {str(e)}")
            return 0
