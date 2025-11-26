# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
from urllib.parse import urlparse, parse_qs

from odoo import models
from odoo.http import request


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    def _stripe_get_inline_form_values(self, *args, sale_order_id=False, **kwargs):
        inline_form_values = super()._stripe_get_inline_form_values(*args, sale_order_id=sale_order_id, **kwargs)
        inline_form_values = json.loads(inline_form_values)

        # if not sale_order_id try fetching from url
        if not sale_order_id:
            url = request.httprequest.url
            parsed_url = urlparse(url)
            params = parse_qs(parsed_url.query)
            sale_order_id = params.get('sale_order_id', [None])[0]
            sale_order_id = sale_order_id and int(sale_order_id)

        sale_order = self.env['sale.order'].browse(sale_order_id).exists()

        if sale_order and sale_order._should_manual_capture():
            inline_form_values.update(capture_method='manual')

        return json.dumps(inline_form_values)
