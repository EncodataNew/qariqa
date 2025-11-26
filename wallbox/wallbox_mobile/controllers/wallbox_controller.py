# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.wallbox_mobile import utils
from werkzeug.exceptions import Unauthorized
from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)


class WallboxController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    @http.route('/v1/my/wallbox/orders', type='http', auth='none', methods=['GET'], csrf=False)
    def my_wallbox_orders(self, **kwargs):
        """Get wallbox orders for authenticated user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            orders = request.env['wallbox.order'].with_user(user).search([], order="create_date desc")

            data = []
            for order in orders:
                data.append({
                    'id': order.id,
                    'order_reference': order.name,
                    'state': order.state,
                    'customer': order.customer_id.name,
                    'condominium': order.condominium_id.sudo().condominium_name if order.condominium_id else '',
                    'building': order.building_id.sudo().building_name if order.building_id else '',
                    'parking_space': order.parking_space_id.sudo().name if order.parking_space_id else '',
                    'charging_station': order.charging_station_id.name if order.charging_station_id else '',
                    'product_id': order.product_id.name,
                    'service_notes': order.service_notes,
                    'installation_date': str(order.installation_date) if order.installation_date else '',
                    'installation_state': order.installation_state,
                    'subscription_exp_date': str(order.subscription_exp_date) if order.subscription_exp_date else '',
                    'sale_order_id': order.sale_order_id.name if order.sale_order_id else '',
                    'date_order': str(order.date_order) if order.date_order else '',
                    'amount_total': order.amount_total,
                    'currency_id': order.currency_id.name if order.currency_id else '',
                    'serial_number': order.serial_number,
                    'invoice_status': order.invoice_status,
                })

            result = {
                'status': True,
                'orders': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/orders", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching wallbox orders: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/my/wallbox/subscriptions', type='http', auth='none', methods=['GET'], csrf=False)
    def my_wallbox_subscriptions(self, **kwargs):
        """Get wallbox subscriptions for authenticated user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            subscriptions = request.env['wallbox.subscription'].with_user(user).search([], order="create_date desc")

            data = []
            for sub in subscriptions:
                data.append({
                    'id': sub.id,
                    'name': sub.name,
                    'wallbox_order_id': sub.wallbox_order_id.id,
                    'product_id': sub.product_id.id,
                    'sale_order_id': sub.sale_order_id.id if sub.sale_order_id else False,
                    'product': sub.product_id.name,
                    'start_date': utils._format_date(sub.start_date),
                    'end_date': utils._format_date(sub.end_date),
                    'state': sub.state,
                })

            result = {
                'status': True,
                'subscriptions': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/subscriptions", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching subscriptions: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/my/wallbox/installations', type='http', auth='none', methods=['GET'], csrf=False)
    def my_wallbox_installations(self, **kwargs):
        """Get installations for user or technician"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            installations = request.env['wallbox.installation'].with_user(user).search([], order="create_date desc")

            data = []
            for inst in installations:
                data.append({
                    'id': inst.id,
                    'name': inst.name,
                    'state': inst.state,
                    'wallbox_order_id': inst.order_id.id,
                    'customer_id': inst.customer_id.id,
                    'installation_technician': inst.installation_technician_id.name,
                    'charger_id': inst.charger_id,
                    'condominium_id': inst.condominium_id.id if inst.condominium_id else False,
                    'building_id': inst.building_id.id if inst.building_id else False,
                    'parking_space_id': inst.parking_space_id.id if inst.parking_space_id else False,
                    'charging_station': inst.charging_station_id.name if inst.charging_station_id else False,
                    'requested_installation_date': utils._format_date(inst.requested_installation_date),
                    'scheduled_installation_date': utils._format_date(inst.scheduled_installation_date),
                    'actual_installation_date': utils._format_date(inst.actual_installation_date),
                    'installation_duration': inst.installation_duration,
                    'reservation_requested': inst.reservation_requested,
                    'reservation_date': utils._format_date(inst.reservation_date),
                    'service_notes': inst.service_notes,
                    'customer_confirmation': inst.customer_confirmation,
                    'documentation': inst.documentation,
                    'warranty_period': inst.warranty_period,
                    'rescheduled_date': utils._format_date(inst.rescheduled_date),
                })

            result = {
                'status': True,
                'installations': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/installations", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching installations: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/wallbox/sessions', type='http', auth='none', methods=['GET'], csrf=False)
    def charging_station_sessions(self, **kwargs):
        """Get charging sessions for user or station owner"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            charging_sessions = request.env['wallbox.charging.session'].with_user(user).search([], order="create_date desc")

            session_data = []
            for session in charging_sessions:
                session_data.append({
                    'id': session.id,
                    'transaction_id': session.transaction_id,
                    'charging_station_id': session.charging_station_id.sudo().name,
                    'customer_id': session.customer_id.name,
                    'max_amount_limit': session.max_amount_limit,
                    'start_meter': session.start_meter,
                    'stop_meter': session.stop_meter,
                    'total_energy': session.total_energy,
                    'cost': session.cost,
                    'status': session.status,
                    'created_at': utils._format_date(session.created_at),
                    'updated_at': utils._format_date(session.updated_at),
                    'start_time': utils._format_date(session.start_time),
                    'end_time': utils._format_date(session.end_time),
                    'total_duration': session.total_duration,
                    'request_id': session.request_id.name if session.request_id else '',
                })

            result = {
                'status': True,
                'charging_sessions': session_data,
                'count': len(session_data)
            }

            utils._log_api_error(api_name="/v1/wallbox/sessions", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching charging sessions: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )
