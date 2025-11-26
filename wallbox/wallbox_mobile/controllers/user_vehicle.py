# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
import logging
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized

from odoo import http
from odoo.http import request, Response
from odoo.addons.web.controllers.utils import ensure_db
from odoo.exceptions import ValidationError

from odoo.addons.wallbox_mobile import utils

_logger = logging.getLogger(__name__)

class VehicleController(http.Controller):

    @http.route('/v1/vehicles', type='http', auth='none', methods=['GET'], csrf=False)
    def list_vehicles(self, **kwargs):
        """List all vehicles (GET request with no body required)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return Response(
                    json.dumps(user),
                    status=401,  # Unauthorized
                    mimetype='application/json'
                )

            vehicles = request.env['user.vehicle'].with_user(user).search([])
            vehicle_list = [self._prepare_vehicle_data(vehicle) for vehicle in vehicles]

            data = {
                'status': True,
                'vehicles': vehicle_list,
                'count': len(vehicle_list)
            }

            utils._log_api_error(api_name="/v1/vehicles", error_code="SUCCESS", error_description="No Error", json_parameters=data, user=user)

            return Response(
                json.dumps(data),
                status=200,
                mimetype='application/json'
            )

        except Exception as e:
            _logger.error("Error listing vehicles: %s", str(e))
            return Response(
                json.dumps(utils._error_response('INTERNAL_ERROR', str(e))),
                status=500,
                mimetype='application/json'
            )

    @http.route('/v1/vehicles', type='json', auth='none', methods=['POST'], csrf=False)
    def create_vehicle(self, **kwargs):
        """Create a new vehicle with optional fields"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user
            data = json.loads(request.httprequest.data)

            # Validate required fields
            required_fields = ['name', 'brand', 'model', 'licence_plate']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return utils._error_response('VALIDATION_ERROR', 
                    f'Missing required fields: {", ".join(missing_fields)}')

            # Prepare vehicle data with all optional fields
            vehicle_data = {
                'name': data['name'],
                'licence_plate': data['licence_plate'],
                'partner_id': user.partner_id.id,
                'brand': data.get('brand'),
                'model': data.get('model'),
                'charging_power': data.get('charging_power'),
                'connector_type': data.get('connector_type'),
                # Add the requested optional fields
                'emissions': data.get('emissions'),
                'consumption': data.get('consumption'),
                'autonomy': data.get('autonomy'),
                'battery_capacity': data.get('battery_capacity'),
                'vehicle_type': data.get('vehicle_type'),
                'fuel_type': data.get('fuel_type'),
                'is_default': data.get('is_default')
            }

            # Create vehicle
            vehicle = request.env['user.vehicle'].with_user(user).create(vehicle_data)

            # make is_default = False to other vehicles if current vehicle is_default = True
            if vehicle.is_default:
                other_vehicles = request.env['user.vehicle'].with_user(user).search([('id', '!=', vehicle.id)])
                other_vehicles.is_default = False

            # Mobile Notification 
            notification_model = request.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(user, 'New vehicle added to profile.')

            result = {
                'status': True,
                'message': 'Vehicle created successfully',
                'vehicle': self._prepare_vehicle_data(vehicle),
            }

            utils._log_api_error(api_name="/v1/vehicles", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.error("Error creating vehicle: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/vehicles/<int:vehicle_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_vehicle(self, vehicle_id, **kwargs):
        """Get vehicle details (HTTP GET)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return Response(
                    json.dumps(user),
                    status=401,  # Unauthorized
                    mimetype='application/json'
                )

            vehicle = self._get_user_vehicle(user, vehicle_id)

            data = {
                'status': True,
                'vehicle': self._prepare_vehicle_data(vehicle)
            }

            utils._log_api_error(api_name="/v1/vehicles/<int:vehicle_id>", error_code="SUCCESS", error_description="No Error", json_parameters=data, user=user)

            return Response(
                json.dumps(data),
                status=200,
                mimetype='application/json'
            )

        except NotFound as e:
            return Response(
                json.dumps(utils._error_response('RESOURCE_NOT_FOUND', str(e))),
                status=404,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error("Error getting vehicle %s: %s", vehicle_id, str(e))
            return Response(
                json.dumps(utils._error_response('INTERNAL_ERROR', str(e))),
                status=500,
                mimetype='application/json'
            )

    @http.route('/v1/vehicles/<int:vehicle_id>', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_vehicle(self, vehicle_id, **kwargs):
        """Update vehicle information"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user
            vehicle = self._get_user_vehicle(user, vehicle_id)
            data = json.loads(request.httprequest.data)

            # Prepare update data with all optional fields
            update_data = {}
            optional_fields = [
                'name', 'licence_plate', 'brand', 'model', 
                'charging_power', 'connector_type', 'emissions',
                'consumption', 'autonomy', 'batteryCapacity',
                'vehicleType', 'fuelType', 'is_default'
            ]

            for field in optional_fields:
                if field in data:
                    # Convert camelCase to snake_case for Odoo fields
                    odoo_field = field[0].lower() + ''.join(
                        f'_{c.lower()}' if c.isupper() else c 
                        for c in field[1:]
                    )
                    update_data[odoo_field] = data[field]

            # Update vehicle
            vehicle.write(update_data)
            if vehicle.is_default:
                other_vehicles = request.env['user.vehicle'].with_user(user).search([('id', '!=', vehicle.id)])
                other_vehicles.is_default = False

            result = {
                'status': True,
                'message': 'Vehicle updated successfully',
                'result': self._prepare_vehicle_data(vehicle)
            }

            utils._log_api_error(api_name="/v1/vehicles/<int:vehicle_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.error("Error updating vehicle %s: %s", vehicle_id, str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/vehicles/<int:vehicle_id>', type='json', auth='none', methods=['DELETE'], csrf=False)
    def delete_vehicle(self, vehicle_id, **kwargs):
        """Delete a vehicle"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user
            vehicle = self._get_user_vehicle(user, vehicle_id)

            if vehicle.request_charging_ids:
                return utils._error_response('VEHICLE_HAS_CHARGING_REQUEST', 'You can not delete the vehicle which is set in any charging request.')

            vehicle.unlink()

            # Mobile Notification
            notification_model = request.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(user, 'Vehicle removed from profile.')

            result = {
                'status': True,
                'message': 'Vehicle deleted successfully'
            }

            utils._log_api_error(api_name="/v1/vehicles/<int:vehicle_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except Exception as e:
            _logger.error("Error deleting vehicle %s: %s", vehicle_id, str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    def _get_user_vehicle(self, user, vehicle_id):
        """Helper to get vehicle and verify ownership"""
        vehicle = request.env['user.vehicle'].sudo().search([
            ('id', '=', vehicle_id),
            ('partner_id', '=', user.partner_id.id)
        ], limit=1)

        if not vehicle:
            raise NotFound('Vehicle not found or access denied')
        return vehicle

    def _prepare_vehicle_data(self, vehicle):
        """Standardize vehicle data format"""
        return {
            'id': vehicle.id,
            'name': vehicle.name,
            'brand': vehicle.brand,
            'model': vehicle.model,
            'licence_plate': vehicle.licence_plate,
            'charging_power': vehicle.charging_power,
            'connector_type': vehicle.connector_type,
            # Include all optional fields
            'emissions': vehicle.emissions,
            'consumption': vehicle.consumption,
            'autonomy': vehicle.autonomy,
            'batteryCapacity': vehicle.battery_capacity,
            'vehicleType': vehicle.vehicle_type,
            'fuelType': vehicle.fuel_type,
            'is_default': vehicle.is_default,
        }
