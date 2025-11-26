# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from datetime import timedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class WallboxInstallation(models.Model):
    _inherit = 'wallbox.installation'


    def action_complete(self):
        super().action_complete()
        for installation in self:
            installation._update_subscription_date_on_complation()

    def _update_subscription_date_on_complation(self):
        """ Update related subscriptions date after instalation is completed. """
        self.ensure_one()
        related_subscriptions = self.order_id.sudo().subscription_ids.sudo()
        previous_subscription = False
        for sub in related_subscriptions:
            if not previous_subscription:
                sub.start_date = self.actual_installation_date.date() + timedelta(days=1)
            else:
                sub.start_date = previous_subscription.end_date + timedelta(days=1)

            sub.end_date = sub.sale_order_id._calculate_subscription_end_date(
                sub.start_date,
                sub.sale_order_line_id.product_template_id
            )
            previous_subscription = sub
