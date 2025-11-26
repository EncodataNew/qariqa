# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wallbox_amount_to_capture = fields.Float("Amount to capture")

    def _should_manual_capture(self):
        """Hook to make sale order's transaction manual capture. """
        self.ensure_one()

        return bool(self.request_charging_id) # (For testing)
