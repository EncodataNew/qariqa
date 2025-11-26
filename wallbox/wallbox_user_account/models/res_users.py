# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from ast import literal_eval

from odoo import api, fields, models, _
from odoo.addons.auth_signup.models.res_partner import SignupError


class ResUsers(models.Model):
    _inherit = 'res.users'

    reseller = fields.Boolean(string='Is Reseller')
    wallbox_user = fields.Boolean(string='Is Wallbox User')

    def _create_user_from_template(self, values):
        # temperary hack - make all user to wallbox_user
        template_user_id = False
        if values.get('wallbox_user') or self.env.context.get('is_wallbox_user'):
            template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('wallbox_user_account.template_wallbox_user_account', 'False'))
        if self.env.context.get('is_technician'):
            template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('wallbox_user_account.template_wallbox_technician_account', 'False'))
        if self.env.context.get('is_condominium_owner'):
            template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('wallbox_user_account.template_wallbox_condominium_account', 'False'))
        if not template_user_id:
            template_user_id = literal_eval(self.env['ir.config_parameter'].sudo().get_param('base.template_portal_user_id', 'False'))
        template_user = self.browse(template_user_id)
        if not template_user.exists():
            raise ValueError(_('Signup: invalid template user'))

        if not values.get('login'):
            raise ValueError(_('Signup: no login given for new user'))
        if not values.get('partner_id') and not values.get('name'):
            raise ValueError(_('Signup: no name or partner given for new user'))

        # create a copy of the template user (attached to a specific partner_id if given)
        values['active'] = True
        try:
            with self.env.cr.savepoint():
                return template_user.with_context(no_reset_password=True).copy(values)
        except Exception as e:
            # copy may failed if asked login is not available.
            raise SignupError(str(e))

    @api.model_create_multi
    def create(self, vals_list):
        users = super(ResUsers, self).create(vals_list)
        for user in users:
            if user.wallbox_user and user.partner_id:
                user.partner_id.write({'is_wallbox_user': True})
        return users

    def write(self, vals):
        res = super(ResUsers, self).write(vals)
        if 'wallbox_user' in vals:
            for user in self:
                if user.partner_id:
                    user.partner_id.write({'is_wallbox_user': vals['wallbox_user']})
        return res
