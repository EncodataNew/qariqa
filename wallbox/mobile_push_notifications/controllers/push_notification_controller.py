# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
from odoo import http
from odoo.http import request

class PushNotificationController(http.Controller):

    @http.route('/push/send_notification', type='json', auth='user', methods=['POST'])
    def send_notification(self, user_id=None, message=None, **kwargs):

        data = json.loads(request.httprequest.data)
        user_id = data.get('user_id')
        message = data.get('message')

        print("\n\n\n\n>>>>>>>>>>> send_notification", self)
        print(">>>>>>>>>>> user_id", user_id)
        print(">>>>>>>>>>> message", message)
        if not user_id or not message:
            return {'success': False, 'error': 'user_id and message are required'}

        user = request.env['res.users'].sudo().browse(int(user_id))
        if not user.exists():
            return {'success': False, 'error': 'User not found'}

        notification_model = request.env['push.notification'].sudo()
        success = notification_model.send_expo_notification(user, message)

        return {'success': success}
