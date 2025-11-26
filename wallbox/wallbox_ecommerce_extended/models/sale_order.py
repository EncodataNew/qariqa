# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    wallbox_order_id = fields.Many2one('wallbox.order', string='Wallbox Order', copy=False, tracking=True)
    has_wallbox_device = fields.Boolean(compute='_compute_has_wallbox_device', store=True,
        help='Check in current order for has wallbox or not.')
    has_subscription = fields.Boolean(compute='_compute_has_subscription', store=True,
        help='Check in current order for has subscription or not.')
    is_first_purchase = fields.Boolean(compute='_compute_is_first_purchase',
        help='Is this the customer\'s first purchase?')
    request_charging_id = fields.Many2one('request.charging', string='Request Charging', tracking=True)

    @api.depends('partner_id')
    def _compute_is_first_purchase(self):
        for order in self:
            order.is_first_purchase = not self.env['sale.order'].search_count([
                ('partner_id', '=', order.partner_id.id),
                ('state', 'not in', ['draft', 'cancel']),
                ('id', '!=', order.id)
            ])

    @api.depends('order_line.product_template_id')
    def _compute_has_wallbox_device(self):
        for order in self:
            order.has_wallbox_device = any(
                line.product_template_id.is_wallbox_device 
                for line in order.order_line
            )

    @api.depends('order_line.product_template_id')
    def _compute_has_subscription(self):
        for order in self:
            order.has_subscription = any(
                line.product_template_id.is_subscription 
                for line in order.order_line
            )

    @api.constrains('order_line')
    def _check_first_purchase_requirements(self):
        for order in self:
            if order.is_first_purchase and order.website_id:
                if not order.has_wallbox_device:
                    raise ValidationError(_(
                        "First purchase must include a Wallbox device"
                    ))
                if not order.has_subscription:
                    raise ValidationError(_(
                        "First purchase must include a subscription"
                    ))

    def action_confirm(self):
        """Override confirm to create wallbox order"""
        # Validate first purchase requirements
        if self.is_first_purchase and self.website_id:
            if not self.has_wallbox_device or not self.has_subscription:
                raise UserError(_(
                    "First purchase must include both a Wallbox device and subscription"
                ))

        res = super().action_confirm()

        for order in self:
            if order.has_wallbox_device and not order.wallbox_order_id:
                wallbox_order = order._create_wallbox_order()

                if order.has_subscription:
                    order._link_subscriptions_to_wallbox(wallbox_order)

            elif not order.has_wallbox_device and order.has_subscription:
                existing_wallbox = self.env['wallbox.order'].search([
                    ('customer_id', '=', order.partner_id.id),
                    ('partner_shipping_id', '=', order.partner_shipping_id.id)
                ], limit=1)

                if existing_wallbox:
                    order.wallbox_order_id = existing_wallbox.id
                    if order.has_subscription:
                        order._link_subscriptions_to_wallbox(existing_wallbox)

        return res

    def _create_wallbox_order(self):
        """Create wallbox order from sale order with address handling"""
        self.ensure_one()

        wallbox_line = self.order_line.filtered(
            lambda l: l.product_template_id.is_wallbox_device
        )[:1]

        if not wallbox_line:
            return False

        wallbox_vals = {
            'name': self.env['ir.sequence'].next_by_code('wallbox.order') or _('New'),
            'customer_id': self.partner_id.id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'product_id': wallbox_line.product_template_id.id,
            'state': 'confirmed',
            'sale_order_id': self.id,
        }
        wallbox_order = self.env['wallbox.order'].create(wallbox_vals)
        self.wallbox_order_id = wallbox_order.id

        return wallbox_order

    def _link_subscriptions_to_wallbox(self, wallbox_order):
        """Link subscription products to wallbox order with dynamic dates"""
        subscription_lines = self.order_line.filtered(
            lambda l: l.product_template_id.is_subscription)

        if not subscription_lines:
            return False

        # Get all existing subscriptions for this wallbox ordered by end date
        existing_subs = self.env['wallbox.subscription'].search([
            ('wallbox_order_id', '=', wallbox_order.id),
            ('state', 'in', ['active', 'expired'])  # Consider both active and expired subscriptions
        ], order='end_date desc')

        # Prepare all subscription records to create
        subscriptions_to_create = []
        today = fields.Date.today()

        for line in subscription_lines:
            # Find most recent subscription of any type for this wallbox
            latest_sub = existing_subs[:1] if existing_subs else False

            if latest_sub:
                # Handle existing subscription
                if latest_sub.end_date < today:
                    # Subscription expired - create new with current date
                    start_date = today
                else:
                    # Subscription still active - create new starting after it ends
                    start_date = latest_sub.end_date + relativedelta(days=1)
            else:
                # No existing subscription - start from today
                start_date = today

            # Calculate end date based on product settings
            end_date = self._calculate_subscription_end_date(
                start_date, 
                line.product_template_id
            )

            subscriptions_to_create.append({
                'wallbox_order_id': wallbox_order.id,
                'product_id': line.product_template_id.id,
                'sale_order_line_id': line.id,
                'start_date': start_date,
                'end_date': end_date,
            })

        # Create all subscriptions in a single operation
        if subscriptions_to_create:
            return self.env['wallbox.subscription'].sudo().create(subscriptions_to_create)
        return False

    def _calculate_subscription_end_date(self, start_date, product):
        """Calculate end date based on product's subscription settings"""
        start_date = fields.Date.from_string(start_date)
        duration = product.subscription_duration
        unit = product.subscription_unit

        if unit == 'days':
            return start_date + relativedelta(days=duration)
        elif unit == 'weeks':
            return start_date + relativedelta(weeks=duration)
        elif unit == 'months':
            return start_date + relativedelta(months=duration)
        elif unit == 'years':
            return start_date + relativedelta(years=duration)
        return start_date

    # Sale order which is created from charging id can not be deleted
    def unlink(self):
        for record in self:
            if record.request_charging_id:
                raise ValidationError(_('You can not delete the sale order which is created from Charging Request.'))
        return super().unlink()
