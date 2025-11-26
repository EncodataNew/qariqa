# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
import logging
from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.exceptions import AccessDenied

_logger = logging.getLogger(__name__)


class WallboxLogController(http.Controller):

    def _validate_api_token(self):
        """Validate the Bearer token from request headers"""
        auth_header = request.httprequest.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AccessDenied("Invalid authorization header")

        incoming_token = auth_header[7:]  # Remove 'Bearer ' prefix
        stored_token = request.env['ir.config_parameter'].sudo().get_param('cms.api.token')

        if not stored_token:
            raise AccessDenied("API token not configured in system parameters")

        if incoming_token != stored_token:
            raise AccessDenied("Invalid access token")

    @http.route('/api/wallbox/logs', type='json', auth='none', methods=['POST'], csrf=False)
    def receive_wallbox_logs(self, **post):
        """Endpoint to receive wallbox logs from CMS server"""
        try:
            # 1. Validate authentication
            self._validate_api_token()

            # 2. Parse and validate incoming data
            data = json.loads(request.httprequest.data)
            if not data:
                return {"error": "No data received"}, 400

            required_fields = ['message', 'payload', 'charger_id', 'direction']
            if not all(field in data for field in required_fields):
                return {"error": f"Missing required fields. Required: {required_fields}"}, 400

            # 3. Prepare log values
            log_vals = {
                'message': data['message'],
                'payload': json.dumps(data['payload']) if isinstance(data['payload'], dict) else str(data['payload']),
                'charger_id': data['charger_id'],
                'direction': data['direction'],
                'not_necessary': data['not_necessary']
            }

            # 4. Handle datetime fields with proper format conversion
            datetime_fields = ['created_at', 'updated_at']
            for field in datetime_fields:
                if field in data and data[field]:
                    try:
                        # Parse ISO format and convert to Odoo's expected format
                        dt = datetime.strptime(data[field], '%Y-%m-%dT%H:%M:%SZ')
                        log_vals[field] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError as e:
                        _logger.warning(f"Invalid datetime format for {field}: {data[field]}")
                        continue

            # 5. Create log record
            charging_station_id = request.env['charging.station'].sudo().search([('charger_id', '=', data['charger_id'])], limit=1)
            log_vals['charging_station_id'] = charging_station_id.id

            log = request.env['wallbox.log'].sudo().create(log_vals)
            _logger.info(f"Created wallbox log ID {log.id} for charger {data['charger_id']}")

            return {"success": True, "log_id": log.id}, 200

        except AccessDenied as e:
            _logger.error(f"Authentication failed: {str(e)}")
            return {"error": str(e)}, 401
        except Exception as e:
            _logger.error(f"Error processing wallbox log: {str(e)}")
            return {"error": str(e)}, 500

    @http.route('/api/wallbox/sessions', type='json', auth='none', methods=['POST'], csrf=False)
    def receive_charging_sessions(self, **post):
        """Endpoint to receive charging session data from CMS server
        Expected JSON payload format:
        {
            "transaction_id": "TRANS123",
            "charging_station_id": "CHARGER123",
            "customer_id": 42,
            "max_amount_limit": 10.5,
            "start_meter": 0.0,
            "stop_meter": 5.3,
            "total_energy": 5.3,
            "cost": 15.9,
            "status": "Ended",
            "created_at": "2023-05-29T10:30:00Z",
            "updated_at": "2023-05-29T11:30:00Z",
            "vehicle_id": 1,
            "start_time": "2023-05-29T10:30:00Z",
            "end_time": "2023-05-29T11:30:00Z",
            "request_id": 5,
            "total_duration": "1 Hour 5 Minutes",
        }
        """
        try:
            # 1. Validate authentication
            self._validate_api_token()

            # 2. Parse and validate incoming data
            data = json.loads(request.httprequest.data)
            if not data:
                return {"error": "No data received"}, 400

            required_fields = ['transaction_id', 'charging_station_id', 'customer_id', 'status']
            if not all(field in data for field in required_fields):
                return {"error": f"Missing required fields. Required: {required_fields}"}, 400

            # 3. Find or create charging station
            charging_station = request.env['charging.station'].sudo().search([
                ('charger_id', '=', data['charging_station_id'])
            ], limit=1)

            if not charging_station:
                return {"error": f"Charging station {data['charging_station_id']} not found"}, 404

            # 4. Prepare session values
            session_vals = {
                'transaction_id': data['transaction_id'],
                'charging_station_id': charging_station.id,
                'customer_id': data['customer_id'],
                'status': data['status'],
                'request_id': data.get('request_id'),
                'total_duration': data.get('total_duration'),
            }

            # Optional fields with defaults
            optional_fields = [
                'max_amount_limit', 'start_meter', 'stop_meter',
                'total_energy', 'cost', 'vehicle_id'
            ]
            for field in optional_fields:
                if field in data:
                    session_vals[field] = data[field]

            # Handle datetime fields
            datetime_fields = ['created_at', 'updated_at', 'start_time', 'end_time']
            for field in datetime_fields:
                if field in data and data[field]:
                    try:
                        session_vals[field] = datetime.strptime(
                            data[field], '%Y-%m-%dT%H:%M:%SZ'
                        )
                    except (ValueError, TypeError):
                        _logger.warning(f"Invalid datetime format for field {field}: {data[field]}")

            # 5. Find existing session or create new one
            existing_session = request.env['wallbox.charging.session'].sudo().search([
                ('transaction_id', '=', data['transaction_id'])
            ], limit=1)

            if existing_session:
                # Update existing session
                existing_session.write(session_vals)
                session = existing_session
                action = 'updated'

                if existing_session.request_id:
                    request_id = existing_session.request_id
                    request_id.sale_order_id.order_line.price_unit = data.get('cost')

                    if data.get('status') in ('Ended', 'Failed'):
                        if request_id.transaction_state == 'authorized':
                            request_id.sale_order_id.wallbox_amount_to_capture = data.get('cost')
                            request_id.sale_order_id.payment_action_capture()
                        request_id.request_status = 'completed'

                        # Mobile Notification
                        notification_model = request.env['push.notification'].sudo()

                        if data.get('status') == 'Ended':
                            success = notification_model.send_expo_notification(request_id.request_user_id.user_id or request_id.request_user_id.user_ids[0], 'Charging completed.')

                        if data.get('status') == 'Failed':
                            success = notification_model.send_expo_notification(request_id.request_user_id.user_id or request_id.request_user_id.user_ids[0], 'Charging failed (technical issue or authorization).')

            else:
                # Create new session
                session = request.env['wallbox.charging.session'].sudo().create(session_vals)
                if data.get('request_id'):
                    request_id = request.env['request.charging'].sudo().search([('id', '=', data.get('request_id'))], limit=1)
                    if request_id:
                        request_id.request_charging_session_id = session.id
                        request_id.sale_order_id.order_line.price_unit = data.get('cost')
                action = 'created'

            _logger.info(
                f"{action.capitalize()} charging session {session.transaction_id} "
                f"(Transaction ID: {data['transaction_id']})"
            )

            return {
                "success": True,
                "action": action,
                "session_id": session.id,
                "session_name": session.transaction_id
            }, 200

        except AccessDenied as e:
            _logger.error(f"Authentication failed: {str(e)}")
            return {"error": str(e)}, 401
        except Exception as e:
            _logger.error(f"Error processing charging session: {str(e)}")
            return {"error": str(e)}, 500

    @http.route('/api/wallbox/status-update', type='json', auth='none', methods=['POST'], csrf=False)
    def receive_status_update(self, **post):
        """Endpoint to receive charging station status updates from CMS server
        Expected JSON payload format:
        {
            "charger_id": "CHARGER123",
            "status": "Available",
        }
        """
        try:
            # 1. Validate authentication
            self._validate_api_token()

            # 2. Parse and validate incoming data
            data = json.loads(request.httprequest.data)
            if not data:
                return {"error": "No data received"}, 400

            required_fields = ['charger_id', 'status']
            if not all(field in data for field in required_fields):
                return {"error": f"Missing required fields. Required: {required_fields}"}, 400

            # 3. Find charging station
            charging_station = request.env['charging.station'].sudo().search([
                ('charger_id', '=', data['charger_id'])
            ], limit=1)

            if not charging_station:
                return {"error": f"Charging station {data['charger_id']} not found"}, 404

            # 4. Validate status value
            valid_statuses = dict(charging_station._fields['status'].selection).keys()
            if data['status'] not in valid_statuses:
                return {
                    "error": f"Invalid status value. Valid values are: {list(valid_statuses)}"
                }, 400

            # 5. Prepare update values
            update_vals = {
                'status': data['status']
            }

            # 6. Update charging station
            charging_station.write(update_vals)
            _logger.info(
                f"Updated status for charging station {charging_station.charger_id} "
                f"to {data['status']}"
            )

            return {
                "success": True,
                "station_id": charging_station.id,
                "charger_id": charging_station.charger_id,
                "new_status": charging_station.status
            }, 200

        except AccessDenied as e:
            _logger.error(f"Authentication failed: {str(e)}")
            return {"error": str(e)}, 401
        except Exception as e:
            _logger.error(f"Error processing status update: {str(e)}")
            return {"error": str(e)}, 500
