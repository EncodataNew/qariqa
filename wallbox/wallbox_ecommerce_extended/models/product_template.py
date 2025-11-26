# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_subscription = fields.Boolean(string="Is Subscription?")
    is_guest_subscription = fields.Boolean(
        string="Is Guest Subscription?",
        help="Check this if the subscription is for guest users"
    )

    subscription_duration = fields.Integer(
        string="Duration Value",
        help="Duration of the subscription period"
    )
    subscription_unit = fields.Selection([
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years')
    ], string="Duration Unit", default='months')

    @api.constrains('is_subscription', 'subscription_duration')
    def _check_subscription_duration(self):
        for product in self:
            if (product.is_subscription or product.is_guest_subscription) and (not product.subscription_duration or product.subscription_duration <= 0):
                raise ValidationError(_(
                    "Subscription products must have a positive duration value"
                ))

    @api.constrains('is_wallbox_device', 'is_subscription', 'is_guest_subscription')
    def _check_product_type(self):
        for product in self:
            if product.is_wallbox_device and (product.is_subscription or product.is_guest_subscription):
                raise ValidationError(_(
                    "A product cannot be both a wallbox device and a subscription"
                ))
            if product.is_subscription and product.is_guest_subscription:
                raise ValidationError(_(
                    "A product cannot be both a regular subscription and a guest subscription"
                ))

            if (product.is_subscription or product.is_guest_subscription) and not product.subscription_unit:
                raise ValidationError(_(
                    "A Subscription product must have 'Duration Unit'"
                ))
