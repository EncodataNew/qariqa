from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta


class WallboxSubscription(models.Model):
    _name = 'wallbox.subscription'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wallbox Subscription'
    _order = 'end_date desc'

    name = fields.Char(string='Reference', default='New')
    wallbox_order_id = fields.Many2one('wallbox.order',  string='Wallbox Order', required=True, tracking=True)
    product_id = fields.Many2one('product.template', string='Subscription', required=True, domain=[('is_subscription', '=', True)], tracking=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', tracking=True)
    sale_order_line_id = fields.Many2one('sale.order.line', string='Sale Order Line', tracking=True)

    start_date = fields.Date(string='Start Date', required=True, default=fields.Date.today, tracking=True)
    end_date = fields.Date(string='End Date', required=True, tracking=True)
    duration_display = fields.Char(string='Duration', compute='_compute_duration_display')

    state = fields.Selection([
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Status', default='active', index=True, tracking=True)

    @api.depends('product_id.subscription_duration', 'product_id.subscription_unit')
    def _compute_duration_display(self):
        for sub in self:
            if sub.product_id.is_subscription:
                duration = sub.product_id.subscription_duration
                unit = sub.product_id.subscription_unit
                sub.duration_display = f"{duration} {unit}"
            else:
                sub.duration_display = "N/A"

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('wallbox.subscription') or _('New')
        return super().create(vals)

    def _cron_check_expired_subscriptions(self):
        """Daily cron to expire subscriptions"""
        today = fields.Date.today()
        expired = self.search([
            ('end_date', '<', today),
            ('state', '=', 'active')
        ])
        expired.write({'state': 'expired'})

    def action_cancel(self):
        """Cancel subscription"""
        self.ensure_one()
        if self.state == 'active':
            self.write({'state': 'cancelled'})
        else:
            raise UserError(_("Only active subscriptions can be cancelled"))
