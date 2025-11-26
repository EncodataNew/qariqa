# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import requests
import logging
from odoo import models, fields, api

_logger = logging.getLogger(__name__)
# Expo-token : MQU2wS0-xd5p3J2a1_kh__U56GKtuXMKAleOe2qj

class PushNotification(models.Model):
    _name = 'push.notification'
    _description = 'Push Notification Log'

    user_id = fields.Many2one('res.users', string='User')
    message = fields.Text(string='Message')
    ticket_id = fields.Char(string='Expo Ticket ID')
    sent_at = fields.Datetime(string='Sent At', default=fields.Datetime.now)
    status = fields.Selection([
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('error', 'Error'),
    ], string='Status', default='pending')
    error_message = fields.Text(string='Error Message')

    def send_expo_notification(self, user, message):
        """Send push notification via Expo"""
        DeviceToken = self.env['wallbox.device.token']
        tokens = DeviceToken.search([
            ('user_id', '=', user.id),
            ('platform', '=', 'expo'),
            ('active', '=', True),
        ])

        if not tokens:
            _logger.warning(f'User {user.name} has no active Expo tokens.')
            return False

        success_all = True
        for token_rec in tokens:
            payload = {
                'to': token_rec.token,
                'sound': 'default',
                'body': message,
            }
            try:
                response = requests.post(
                    'https://exp.host/--/api/v2/push/send',
                    json=payload,
                    headers={'Content-Type': 'application/json'}
                )
                resp_json = response.json()
                print(">>>>>>>>>>> resp_json", resp_json)

                if response.status_code == 200 and "data" in resp_json:
                    ticket_id = resp_json["data"].get("id")
                    self.create({
                        'user_id': user.id,
                        'message': message,
                        'ticket_id': ticket_id,
                        'status': 'sent' if resp_json["data"].get("status") == "ok" else 'failed',
                        'error_message': resp_json["data"].get("message"),
                    })
                else:
                    _logger.error(f'Expo error: {resp_json}')
                    self.create({
                        'user_id': user.id,
                        'message': message,
                        'status': 'error',
                        'error_message': str(resp_json),
                    })
                    success_all = False

            except Exception as e:
                _logger.error(f'Exception sending notification: {e}')
                self.create({
                    'user_id': user.id,
                    'message': message,
                    'status': 'error',
                    'error_message': str(e),
                })
                success_all = False

        return success_all

    def check_expo_receipts(self):
        """Check delivery receipts for sent notifications"""
        tickets = self.search([('status', '=', 'sent'), ('ticket_id', '!=', False)])
        if not tickets:
            return

        ticket_ids = [t.ticket_id for t in tickets]
        print(">>>>>>>>> ticket_ids", ticket_ids)
        try:
            response = requests.post(
                'https://exp.host/--/api/v2/push/getReceipts',
                json={"ids": ticket_ids},
                headers={'Content-Type': 'application/json'}
            )
            resp_json = response.json()
            print(">>>>>>>>>>> resp_json", resp_json)
            receipts = resp_json.get("data", {})

            for ticket in tickets:
                receipt = receipts.get(ticket.ticket_id)
                if not receipt:
                    continue
                if receipt.get("status") == "ok":
                    ticket.status = "sent"
                else:
                    ticket.status = "failed"
                    ticket.error_message = receipt.get("message")
        except Exception as e:
            _logger.error(f'Error checking receipts: {e}')
