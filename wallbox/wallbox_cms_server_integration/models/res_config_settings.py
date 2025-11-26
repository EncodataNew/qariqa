# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    cms_api_url = fields.Char(
        string='CMS API URL',
        help='Base URL for CMS API endpoint',
        config_parameter='cms.api.url'
    )

    cms_api_token = fields.Char(
        string='CMS API Token',
        help='Authentication token for CMS API',
        config_parameter='cms.api.token'
    )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            cms_api_url=params.get_param('cms.api.url', default=''),
            cms_api_token=params.get_param('cms.api.token', default=''),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env['ir.config_parameter'].sudo().set_param('cms.api.url', self.cms_api_url or '')
        self.env['ir.config_parameter'].sudo().set_param('cms.api.token', self.cms_api_token or '')
