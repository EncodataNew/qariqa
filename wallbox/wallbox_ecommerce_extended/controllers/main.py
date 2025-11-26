# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import http
from odoo.http import request
from odoo.tools.translate import _
from odoo.exceptions import ValidationError
from odoo.addons.website_sale.controllers.main import WebsiteSale

class WebsiteSaleSubscription(WebsiteSale):

    @http.route('', type='http', methods=['GET'], auth='public', website=True, sitemap=False)
    def shop_checkout(self, try_skip_step=None, **query_params):
        order_sudo = request.website.sale_get_order()
        partner = order_sudo.partner_id

        # Skip validation for empty carts
        if not order_sudo or not order_sudo.order_line:
            return super().shop_checkout(try_skip_step, **query_params)

        # Check wallbox subscription requirements
        has_wallbox = any(line.product_id.is_wallbox_device for line in order_sudo.order_line)
        has_subscription = any(line.product_id.is_subscription for line in order_sudo.order_line)

        # First-time purchase validation
        partner_wallbox = request.env['stock.lot.report'].sudo().search([
            ("has_return", "=", False),
            ("partner_id", "=", partner.id),
        ])
        # print("\n\n\n >>>>>>>>>>>> partner_wallbox", partner_wallbox)
        # if not partner.has_wallbox:
        if not partner_wallbox:
            if has_wallbox and not has_subscription:
                return request.redirect('/shop/cart?error=subscription_required')
            elif not has_wallbox and has_subscription:
                return request.redirect('/shop/cart?error=wallbox_required')

        # Continue with normal checkout flow
        return super().shop_checkout(try_skip_step, **query_params)

    @http.route('', type='http', auth="public", website=True, sitemap=False)
    def cart(self, access_token=None, revive='', **post):
        response = super().cart(access_token, revive, **post)
        # Handle our custom error messages
        error = request.httprequest.args.get('error')
        if error:
            if error == 'subscription_required':
                response.qcontext['warning'] = _(
                    "Your first wallbox purchase requires a subscription. "
                    "Please add a subscription to your cart."
                )
            elif error == 'wallbox_required':
                response.qcontext['warning'] = _(
                    "You must purchase a wallbox device before buying subscriptions. "
                    "Please add a wallbox to your cart first."
                )
            elif error == 'existing_wallbox':
                response.qcontext['warning'] = _(
                    "You already have a wallbox at this address. "
                    "Please purchase only subscriptions or choose a different installation address."
                )
        return response

    @http.route('', type='http', auth="public", website=True, sitemap=False)
    def shop_confirm_order(self, **post):
        order_sudo = request.website.sale_get_order()
        partner = order_sudo.partner_id

        # Check if this is a new installation address
        is_new_address = self._check_new_installation_address(order_sudo)

        # Skip validation for empty carts or new installations
        if not order_sudo or not order_sudo.order_line or is_new_address:
            return super().shop_confirm_order(**post)

        # Check wallbox subscription requirements
        has_wallbox = any(line.product_id.is_wallbox_device for line in order_sudo.order_line)
        has_subscription = any(line.product_id.is_subscription for line in order_sudo.order_line)

        # Existing customer validation
        partner_wallbox = request.env['stock.lot.report'].sudo().search([
            ("has_return", "=", False),
            ("partner_id", "=", partner.id),
        ])
        if partner_wallbox and not is_new_address:
            if has_wallbox:
                return request.redirect('/shop/cart?error=existing_wallbox')

        return super().shop_confirm_order(**post)

    def _check_new_installation_address(self, order):
        """Check if shipping address differs from existing installations"""
        partner = order.partner_id
        shipping_address = order.partner_shipping_id

        # Check if this address has any existing wallboxes
        existing_wallboxes = request.env['wallbox.order'].sudo().search([
            ('customer_id', '=', partner.id),
            ('partner_shipping_id', '=', shipping_address.id)
        ])

        return not bool(existing_wallboxes)
