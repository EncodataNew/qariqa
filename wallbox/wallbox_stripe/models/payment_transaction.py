# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
import pprint

from odoo import models

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_stripe.controllers.main import StripeController

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    def _stripe_prepare_payment_intent_payload(self):
        payment_intent_payload = super()._stripe_prepare_payment_intent_payload()
        if len(self.sale_order_ids) == 1 and self.sale_order_ids._should_manual_capture():
            payment_intent_payload.update(capture_method='manual')

        return payment_intent_payload

    def _send_capture_request(self, amount_to_capture=None):
        """ Override of `payment_stripe` to send a capture request to Stripe with amount to capture. """
        if self.provider_code != 'stripe':
            return super()._send_capture_request(amount_to_capture=amount_to_capture)

        related_order = self.sale_order_ids[0]
        if not amount_to_capture and related_order._should_manual_capture() and related_order.wallbox_amount_to_capture:
            orignal_sol_amount = sum(related_order.order_line.mapped('price_unit'))
            related_order.order_line.price_unit = related_order.wallbox_amount_to_capture

            # update transaction amount to amount_to_capture
            self.amount = related_order.wallbox_amount_to_capture

            payment_intent = self.provider_id._stripe_make_request(
                f'payment_intents/{self.provider_reference}/capture',
                payload={
                  "amount_to_capture": payment_utils.to_minor_currency_units(self.amount, self.currency_id)
                },
            )

            _logger.info(
                "capture request response for transaction (amount=%s) with reference %s:\n%s",
                self.reference, self.amount, pprint.pformat(payment_intent)
            )

            notification_data = {'reference': self.reference}
            StripeController._include_payment_intent_in_notification_data(
                payment_intent, notification_data
            )
            self._handle_notification_data('stripe', notification_data)

            return self.env['payment.transaction']

        return super()._send_capture_request(amount_to_capture=amount_to_capture)
