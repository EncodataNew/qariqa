# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import UserError

from collections import defaultdict


class WallBoxChargingSessionWizard(models.TransientModel):
    _name = 'wall.box.charging.session.wizard'
    _description = 'Charging Session Report'

    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    customer_ids = fields.Many2many('res.partner', string='customer')

    def action_print(self):
        charging_station = self.env['charging.station'].browse(self._context.get('active_id'))
        sessions = charging_station.charging_session_ids

        if not self.start_date or not self.end_date:
            raise UserError(_("Please select both Start Date and End Date."))

        if self.customer_ids:
            sessions = sessions.filtered(lambda s: s.customer_id in self.customer_ids)

        # Group sessions by customer
        grouped_session = defaultdict(list)
        for session in sessions:
            grouped_session[session.customer_id.name].append({
                'transaction_id': session.transaction_id,
                'start_meter': session.start_meter,
                'stop_meter': session.stop_meter,
                'total_energy': session.total_energy,
                'start_time': session.start_time,
                'end_time': session.end_time,
                'total_duration': session.total_duration,
                'status': session.status,
                'cost': session.cost,
            })

        return self.env.ref('wallbox_reports.action_report_charging_session').report_action(
            self,
            data={
                'grouped_sessions': dict(grouped_session),
                'charging_station_name': charging_station.name,
                'serial_number': charging_station.serial_number,
                'owner': charging_station.owner_id.name,
                'price_per_kwh': charging_station.price_per_kwh,
                'start_date': self.start_date,
                'end_date': self.end_date,
                'charger_id': charging_station.charger_id,
                'session_count': len(sessions)
            }
        )
