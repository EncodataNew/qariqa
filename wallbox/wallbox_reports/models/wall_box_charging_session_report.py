# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ReportChargingSession(models.AbstractModel):
    _name = 'report.wallbox_reports.report_charging_session_pdf'
    _description = 'Charging Session Pdf'

    @api.model
    def _get_report_values(self, docids, data=None):
        return {
            'doc_ids': docids,
            'doc_model': 'wall.box.charging.session.wizard',
            'data': data or {},  # <== This allows access to grouped_sessions inside QWeb
        }
