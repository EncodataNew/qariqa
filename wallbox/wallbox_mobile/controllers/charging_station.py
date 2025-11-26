# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.wallbox_mobile import utils
from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)


class ChargingStationController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    def _prepare_station_data(self, station):
        """Prepare charging station data dictionary"""
        return {
            'id': station.id,
            'name': station.name,
            'building': station.building_id.sudo().building_name if station.building_id else '',
            'parking_space': station.parking_space_id.sudo().name if station.parking_space_id else '',
            'installation_date': str(station.installation_date) if station.installation_date else '',
            'location': station.location,
            'charging_power': station.charging_power,
            'guest_max_amount_limit': station.guest_max_amount_limit,
            'connector_type': station.connector_type,
            'latitude': station.latitude,
            'longitude': station.longitude,
            'number_of_ports': station.number_of_ports,
            'owner_id': station.owner_id.id if station.owner_id else False,
            'owner_name': station.owner_id.name if station.owner_id else '',
            'access_type': station.access_type,
            'authentication_method': station.authentication_method,
            'energy_source': station.energy_source,
            'billing_system': station.billing_system,
            'last_maintenance_date': str(station.last_maintenance_date) if station.last_maintenance_date else '',
            'next_scheduled_maintenance': str(station.next_scheduled_maintenance) if station.next_scheduled_maintenance else '',
            'reported_issues': station.reported_issues,
            'wallbox_order_id': station.wallbox_order_id.id,
            'number_of_charging_sessions': station.number_of_charging_sessions,
            'total_allowed_users': len(station.allowed_partner_ids),
            'total_rfid_tags': len(station.rfid_tag_ids),
            'charger_id': station.charger_id,
            'price_per_kwh': station.price_per_kwh,
            'status': station.status,
            'total_energy': station.total_energy,
            'total_recharged_cost': station.total_recharged_cost,
            'ws_url': station.ws_url,
        }

    @http.route('/v1/my/wallbox/charging_stations', type='http', auth='none', methods=['GET'], csrf=False)
    def get_charging_stations(self, **kwargs):
        """Get all charging stations for authenticated user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)
                
            stations = request.env['charging.station'].with_user(user).search([], order="create_date desc")
            data = [self._prepare_station_data(station) for station in stations]

            result = {
                'status': True,
                'charging_stations': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/charging_stations", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching charging stations: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/my/wallbox/charging_stations/<int:station_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_charging_station(self, station_id, **kwargs):
        """Get specific charging station by ID"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            station = request.env['charging.station'].with_user(user).browse(station_id)
            if not station.exists():
                return self._json_response(
                    utils._error_response('NOT_FOUND', 'Charging station not found'),
                    404
                )

            result = {
                'status': True,
                'charging_station': self._prepare_station_data(station)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/charging_stations/<int:station_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching charging station: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/my/wallbox/charging_stations/<int:station_id>', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_charging_station(self, station_id, **kwargs):
        """Update charging station information
        PUT /v1/my/wallbox/charging_stations/<id>
        {
            "guest_max_amount_limit": 50,
            "latitude": 40.7128,
            "longitude": -74.0060,
            "price_per_kwh": 0.15
        }
        """
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            station = request.env['charging.station'].with_user(user).browse(station_id)
            if not station.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Charging station not found')

            data = json.loads(request.httprequest.data)

            # Prepare update data with allowed fields
            update_data = {}
            allowed_fields = {
                'guest_max_amount_limit': 'guest_max_amount_limit',
                'latitude': 'latitude',
                'longitude': 'longitude',
                'price_per_kwh': 'price_per_kwh'
            }

            for field, odoo_field in allowed_fields.items():
                if field in data:
                    # Validate field values
                    if field in ['latitude', 'longitude'] and not isinstance(data[field], (int, float)):
                        return utils._error_response('VALIDATION_ERROR', f'{field} must be a number')
                    if field == 'price_per_kwh' and (not isinstance(data[field], (int, float)) or data[field] < 0):
                        return utils._error_response('VALIDATION_ERROR', 'price_per_kwh must be a positive number')
                    if field == 'guest_max_amount_limit' and (not isinstance(data[field], (int, float)) or data[field] < 0):
                        return utils._error_response('VALIDATION_ERROR', 'guest_max_amount_limit must be a positive number')

                    update_data[odoo_field] = data[field]

            if not update_data:
                return utils._error_response('VALIDATION_ERROR', 'No valid fields to update')

            # Update station
            station.write(update_data)

            result = {
                'status': True,
                'message': 'Charging station updated successfully',
                'result': self._prepare_station_data(station)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/charging_stations/<int:station_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except json.JSONDecodeError:
            return utils._error_response('INVALID_JSON', 'Invalid JSON data provided')
        except Exception as e:
            _logger.error("Error updating charging station %s: %s", station_id, str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/my/wallbox/charging_stations/<int:station_id>/sessions', type='http', auth='none', methods=['GET'], csrf=False)
    def wallbox_historical_sessions(self, station_id, **kwargs):
        """Get historical charging sessions for a specific charging station"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            sessions = request.env['wallbox.charging.session'].sudo().search([
                ('charging_station_id', '=', station_id),
                ('status', 'in', ('Ended', 'Failed'))
            ], order="create_date desc")

            data = []
            for session in sessions:
                data.append({
                    'id': session.id,
                    'transaction_id': session.transaction_id,
                    'customer': session.customer_id.name,
                    'total_energy': session.total_energy,
                    'start_meter': session.start_meter,
                    'start_time': utils._format_date(session.start_time),
                    'created_at': utils._format_date(session.created_at),
                    'cost': session.cost,
                    'max_amount_limit': session.max_amount_limit,
                    'status': session.status,
                    'end_time': utils._format_date(session.end_time),
                    'total_duration': session.total_duration,
                    'request_id': session.request_id.id if session.request_id else None,
                })

            result = {
                'status': True,
                'historical_sessions': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/charging_stations/<int:station_id>/sessions", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching historical sessions: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/my/wallbox/charging_stations/<int:station_id>/sessions/ongoing', type='http', auth='none', methods=['GET'], csrf=False)
    def wallbox_ongoing_sessions(self, station_id, **kwargs):
        """Get ongoing charging sessions (0-or-many) for a specific charging station"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            sessions = request.env['wallbox.charging.session'].sudo().search([
                ('charging_station_id', '=', station_id),
                ('status', '=', 'Started'),
            ], order="create_date desc")

            if not sessions:
                return self._json_response({
                    'status': True,
                    'ongoing_sessions': [],
                    'count': 0,
                })

            data = []
            for session in sessions:
                data.append({
                    'id': session.id,
                    'transaction_id': session.transaction_id,
                    'customer': session.customer_id.name,
                    'total_energy': session.total_energy,
                    'start_meter': session.start_meter,
                    'start_time': utils._format_date(session.start_time),
                    'created_at': utils._format_date(session.created_at),
                    'cost': session.cost,
                    'max_amount_limit': session.max_amount_limit,
                    'status': session.status,
                    'end_time': utils._format_date(session.end_time),
                    'total_duration': session.total_duration,
                    'request_id': session.request_id.id if session.request_id else None,
                })

            result = {
                'status': True,
                'ongoing_sessions': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/my/wallbox/charging_stations/<int:station_id>/sessions/ongoing", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching ongoing sessions: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )
