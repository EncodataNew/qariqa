# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.http import request
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as Home


class WallboxUserRegistration(Home):
    def get_auth_signup_qcontext(self):
        qcontext = super().get_auth_signup_qcontext()
        if request.params.get('wallbox_user'):
            qcontext['wallbox_user'] = True
        return qcontext

    def _prepare_signup_values(self, qcontext):
        values = super()._prepare_signup_values(qcontext)
        if qcontext.get('wallbox_user'):
            values['wallbox_user'] = True
        return values
