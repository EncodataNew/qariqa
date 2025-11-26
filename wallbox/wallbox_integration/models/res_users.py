# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ResUsers(models.Model):
    _inherit = 'res.users'

    # Wallbox Users
    registration_date = fields.Date(string="Registration Date")
    last_login_date = fields.Date(string="Last Login Date")
    last_password_change = fields.Date(string="Last Password Change")
    terms_acceptance_date = fields.Date(string="Terms Acceptance Date")
    privacy_policy_acceptance_date = fields.Date(string="Privacy Policy Acceptance Date")
    activity_logs = fields.Text(string="Activity Logs")
    # for activity_logs field we need to make one master table for store user login and logout data and IP Address
    user_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),
        ('admin', 'Administrator')],
        string="User Type"
    )
    account_status = fields.Selection([
        ('active', 'Active'),
        ('suspended', 'Suspended'),
        ('deactivated', 'Deactivated')],
        string="Account Status"
    )
    # TODO MUB : Role field should be security group of wallbox
    role = fields.Selection([
        ('admin', 'Admin'),
        ('user', 'User'),
        ('guest', 'Guest')],
        string="Role"
    )
