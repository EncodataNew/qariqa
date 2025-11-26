# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class WallboxOrder(models.Model):
    _inherit = 'wallbox.order'

    # link sale order flow
    # -----------------------------------------------------------------
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True, tracking=True)
    invoice_status = fields.Selection(related="sale_order_id.invoice_status", string="Invoice Status")
    date_order = fields.Datetime(string='Order Date', related="sale_order_id.date_order")
    amount_total = fields.Monetary(string='Total Amount', related="sale_order_id.amount_total")
    currency_id = fields.Many2one(related="sale_order_id.currency_id")
    serial_number = fields.Char(string='Serial Number', readonly=True, tracking=True)

    subscription_ids = fields.One2many(
        'wallbox.subscription', 
        'wallbox_order_id', 
        string='Subscriptions'
    )
    has_active_subscription = fields.Boolean(
        compute='_compute_has_active_subscription',
        string='Has Active Subscription', tracking=True
    )
    subscription_count = fields.Integer(string='Subscriptions Count', compute="_compute_subscription_count", store=True)

    active_subscription_id = fields.Many2one(
        'wallbox.subscription',
        string='Active Subscription',
        compute='_compute_active_subscription',
        store=True, tracking=True
    )

    partner_shipping_id = fields.Many2one(
        'res.partner',
        string='Installation Address',
        required=True, tracking=True
    )
    subscription_exp_date = fields.Date(
        string='Subscription Expiration Date',
        compute='_compute_subscription_exp_date',
        store=True, tracking=True,
        help="Latest expiration date among all active subscriptions"
    )

    # Update the compute method
    @api.depends('subscription_ids.state', 'subscription_ids.end_date')
    def _compute_subscription_exp_date(self):
        today = fields.Date.today()
        for order in self:
            active_subs = order.subscription_ids.filtered(
                lambda s: s.state == 'active' and s.end_date >= today
            )
            if active_subs:
                order.subscription_exp_date = max(active_subs.mapped('end_date'))
            else:
                order.subscription_exp_date = False

    @api.depends('subscription_ids.state', 'subscription_ids.end_date')
    def _compute_active_subscription(self):
        today = fields.Date.today()
        for order in self:
            active = order.subscription_ids.filtered(
                lambda s: s.state == 'active' and 
                s.start_date <= today and 
                s.end_date >= today
            )
            order.active_subscription_id = active[:1] if active else False

    @api.depends("subscription_ids")
    def _compute_subscription_count(self):
        for rec in self:
            rec.subscription_count = len(rec.subscription_ids)

    @api.depends('subscription_ids.state')
    def _compute_has_active_subscription(self):
        for order in self:
            order.has_active_subscription = any(
                sub.state == 'active' 
                for sub in order.subscription_ids
            )

    def action_view_subscriptions(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Subscriptions',
            'res_model': 'wallbox.subscription',
            'view_mode': 'list,form',
            'domain': [('wallbox_order_id', '=', self.id)],
            'context': {'default_wallbox_order_id': self.id},
        }
    # finish sale order flow
    # ----------------------------------------------------------

    def action_complete(self):
        super().action_complete()
        self.charging_station_id.serial_number = self.serial_number
