# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
import logging
from datetime import datetime, timedelta

from werkzeug.exceptions import NotFound
from odoo import http, fields
from odoo.http import request, Response
from odoo.addons.web.controllers.utils import ensure_db
from odoo.exceptions import ValidationError

from odoo.addons.wallbox_mobile import utils

_logger = logging.getLogger(__name__)


class TripController(http.Controller):
    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data, default=str),
            status=status,
            mimetype='application/json'
        )

    def _prepare_trip_data(self, trip):
        """Return trip payload shaped similar to ITrip interface used by mobile."""
        # waypoints
        wps = []
        for wp in trip.waypoint_ids:
            wps.append({'latitude': wp.latitude, 'longitude': wp.longitude, 'id': wp.id})
        # advised evs
        evs = []
        for ev in trip.advised_evehicle_ids:
            evs.append({
                '_id': ev.id,
                'make': ev.make,
                'model': ev.model,
                'name': ev.name,
                'autonomy': ev.autonomy,
                'mileagePerc': ev.mileage_perc,
                'advisePerc': ev.advise_perc,
            })
        return {
            'id': trip.id,
            'vehicleId': trip.vehicle_id.id if trip.vehicle_id else (trip.vehicle_identifier or False),
            'origin': {'latitude': trip.origin_latitude, 'longitude': trip.origin_longitude},
            'destination': {'latitude': trip.destination_latitude, 'longitude': trip.destination_longitude},
            'waypoints': wps,
            'distance': float(trip.distance) if trip.distance is not None else None,
            'duration': float(trip.duration) if trip.duration is not None else None,
            'date': fields.Datetime.to_string(trip.date) if trip.date else None,
            'pee': trip.pee,
            'saving': {
                'co2': trip.saving_co2,
                'economics': trip.saving_economics,
                'tep': trip.saving_tep,
            },
            'evehicles': evs,
            'isSimulated': bool(trip.is_simulated),
            'isElectric': bool(trip.is_electric),
            'startAutonomy': trip.start_autonomy,
        }

    def _get_user_trip(self, user, trip_id):
        """Return trip record and validate access by vehicle owner or creator."""
        trip = request.env['trip.trip'].sudo().browse(trip_id)
        if not trip.exists():
            raise NotFound('Trip not found')

        # If trip has linked vehicle, ensure vehicle belongs to user's partner
        if trip.vehicle_id:
            if not trip.vehicle_id.partner_id or trip.vehicle_id.partner_id.id != user.partner_id.id:
                raise NotFound('Trip not found or access denied')

        # Otherwise allow if creator is the user (fallback)
        else:
            if trip.create_uid and trip.create_uid.id != user.id:
                raise NotFound('Trip not found or access denied')

        return trip

    @http.route('/v1/trips', type='http', auth='none', methods=['GET'], csrf=False)
    def list_trips(self, **kwargs):
        """
        GET /v1/trips?isSimulated=&vehicleIds=&month=&year=
        Accepts optional query params:
         - isSimulated: 'true'|'false'
         - vehicleIds: comma separated ids
         - month: 1-12
         - year: 4-digit
        """
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            domain = []
            # Filter isSimulated
            is_simulated = kwargs.get('isSimulated')
            if is_simulated is not None:
                if is_simulated.lower() in ('1', 'true', 'yes'):
                    domain.append(('is_simulated', '=', True))
                else:
                    domain.append(('is_simulated', '=', False))

            # vehicleIds
            vehicle_ids = kwargs.get('vehicleIds') or kwargs.get('vehicleIds[]')
            if vehicle_ids:
                # accept comma separated or list-form
                if isinstance(vehicle_ids, str):
                    ids = [int(x) for x in vehicle_ids.split(',') if x.strip().isdigit()]
                elif isinstance(vehicle_ids, (list, tuple)):
                    ids = [int(x) for x in vehicle_ids]
                else:
                    ids = []
                if ids:
                    domain.append(('vehicle_id', 'in', ids))

            # month & year filter on date
            month = kwargs.get('month')
            year = kwargs.get('year')
            if month and year:
                try:
                    m = int(month)
                    y = int(year)
                    start = datetime(y, m, 1)
                    # compute next month start
                    if m == 12:
                        end = datetime(y + 1, 1, 1)
                    else:
                        end = datetime(y, m + 1, 1)
                    domain.append(('date', '>=', fields.Datetime.to_string(start)))
                    domain.append(('date', '<', fields.Datetime.to_string(end)))
                except Exception:
                    # ignore bad month/year
                    pass

            # Search trips - restrict access by vehicle ownership or create_uid check
            # We fetch all candidate trips then filter by ownership to be safe
            candidates = request.env['trip.trip'].sudo().search(domain)
            trips = []
            for t in candidates:
                # allow if vehicle owner == user.partner or creator == user
                allowed = False
                if t.vehicle_id and t.vehicle_id.partner_id and t.vehicle_id.partner_id.id == user.partner_id.id:
                    allowed = True
                elif t.create_uid and t.create_uid.id == user.id:
                    allowed = True
                if allowed:
                    trips.append(t)

            trip_list = [self._prepare_trip_data(t) for t in trips]
            return self._json_response({'status': True, 'trips': trip_list, 'count': len(trip_list)}, 200)

        except Exception as e:
            _logger.exception("Error listing trips: %s", e)
            return self._json_response(utils._error_response('INTERNAL_ERROR', str(e)), 500)

    @http.route('/v1/trips', type='json', auth='none', methods=['POST'], csrf=False)
    def create_trip(self, **kwargs):
        """
        Create trip. Accepts JSON body similar to ITrip.
        """
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)

            # optional: validate presence of essential fields (vehicleId or distance/date)
            # Map payload fields to odoo fields
            vals = {}
            # vehicle
            vehicle_id = data.get('vehicleId') or data.get('vehicle_id')
            if vehicle_id:
                vehicle = request.env['user.vehicle'].with_user(user).sudo().browse(int(vehicle_id))
                if not vehicle.exists() or (vehicle.partner_id and vehicle.partner_id.id != user.partner_id.id):
                    return utils._error_response('ACCESS_DENIED', 'Invalid vehicle')
                vals['vehicle_id'] = vehicle.id

            if data.get('vehicleIdentifier') is not None:
                vals['vehicle_identifier'] = data.get('vehicleIdentifier')

            origin = data.get('origin')
            if origin and isinstance(origin, dict):
                vals['origin_latitude'] = origin.get('latitude')
                vals['origin_longitude'] = origin.get('longitude')

            destination = data.get('destination') or data.get('ddestination') or data.get('destinaton')
            if destination and isinstance(destination, dict):
                vals['destination_latitude'] = destination.get('latitude')
                vals['destination_longitude'] = destination.get('longitude')

            if 'distance' in data:
                vals['distance'] = data.get('distance')
            if 'duration' in data:
                vals['duration'] = data.get('duration')

            if 'date' in data and data.get('date'):
                try:
                    vals['date'] = fields.Datetime.to_datetime(data.get('date'))
                except Exception:
                    vals['date'] = fields.Datetime.context_timestamp(request.env.user, fields.Datetime.now())

            if 'pee' in data:
                vals['pee'] = data.get('pee')

            saving = data.get('saving')
            if saving and isinstance(saving, dict):
                vals['saving_co2'] = saving.get('co2')
                vals['saving_economics'] = saving.get('economics')
                vals['saving_tep'] = saving.get('tep')

            vals['is_simulated'] = bool(data.get('isSimulated', data.get('is_simulated', False)))
            vals['is_electric'] = bool(data.get('isElectric', data.get('is_electric', False)))
            if 'startAutonomy' in data:
                vals['start_autonomy'] = data.get('startAutonomy')

            # Create trip (sudo as user)
            Trip = request.env['trip.trip'].with_user(user).sudo()
            trip = Trip.create(vals)

            # waypoints
            waypoints = data.get('waypoints')
            if waypoints and isinstance(waypoints, list):
                wp_model = request.env['trip.location'].sudo()
                for wp in waypoints:
                    try:
                        wp_model.create({
                            'trip_id': trip.id,
                            'latitude': wp.get('latitude'),
                            'longitude': wp.get('longitude'),
                        })
                    except Exception:
                        _logger.warning('Skipping invalid waypoint payload: %s', wp)

            # advised evehicles
            evehicles = data.get('evehicles')
            if evehicles and isinstance(evehicles, list):
                ev_model = request.env['trip.advised_evehicle'].sudo()
                for ev in evehicles:
                    try:
                        ev_model.create({
                            'trip_id': trip.id,
                            'make': ev.get('make'),
                            'model': ev.get('model'),
                            'name': ev.get('name'),
                            'autonomy': ev.get('autonomy'),
                            'mileage_perc': ev.get('mileagePerc') or ev.get('mileage_perc'),
                            'advise_perc': ev.get('advisePerc') or ev.get('advise_perc'),
                        })
                    except Exception:
                        _logger.warning('Skipping invalid evehicle payload: %s', ev)

            return {
                'status': True,
                'message': 'Trip created successfully',
                'trip': self._prepare_trip_data(trip)
            }

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.exception("Error creating trip: %s", e)
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/trips/<int:trip_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_trip(self, trip_id, **kwargs):
        """Retrieve single trip"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            trip = self._get_user_trip(user, trip_id)
            return self._json_response({'status': True, 'trip': self._prepare_trip_data(trip)}, 200)

        except NotFound as e:
            return self._json_response(utils._error_response('RESOURCE_NOT_FOUND', str(e)), 404)
        except Exception as e:
            _logger.exception("Error getting trip %s: %s", trip_id, e)
            return self._json_response(utils._error_response('INTERNAL_ERROR', str(e)), 500)

    @http.route('/v1/trips/<int:trip_id>', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_trip(self, trip_id, **kwargs):
        """Update trip - accepts partial payload"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            trip = self._get_user_trip(user, trip_id)
            data = json.loads(request.httprequest.data)

            vals = {}
            # vehicle change
            vehicle_id = data.get('vehicleId') or data.get('vehicle_id')
            if vehicle_id:
                vehicle = request.env['user.vehicle'].with_user(user).sudo().browse(int(vehicle_id))
                if not vehicle.exists() or (vehicle.partner_id and vehicle.partner_id.id != user.partner_id.id):
                    return utils._error_response('ACCESS_DENIED', 'Invalid vehicle')
                vals['vehicle_id'] = vehicle.id

            if 'vehicleIdentifier' in data:
                vals['vehicle_identifier'] = data.get('vehicleIdentifier')

            origin = data.get('origin')
            if origin and isinstance(origin, dict):
                vals['origin_latitude'] = origin.get('latitude')
                vals['origin_longitude'] = origin.get('longitude')

            destination = data.get('destination') or data.get('ddestination')
            if destination and isinstance(destination, dict):
                vals['destination_latitude'] = destination.get('latitude')
                vals['destination_longitude'] = destination.get('longitude')

            for f in ('distance', 'duration', 'pee', 'startAutonomy'):
                if f in data:
                    # convert camelCase to snake_case as needed
                    key = f
                    if f == 'startAutonomy':
                        key = 'start_autonomy'
                    vals[key] = data.get(f)

            if 'date' in data and data.get('date'):
                try:
                    vals['date'] = fields.Datetime.to_datetime(data.get('date'))
                except Exception:
                    pass

            saving = data.get('saving')
            if saving and isinstance(saving, dict):
                vals['saving_co2'] = saving.get('co2')
                vals['saving_economics'] = saving.get('economics')
                vals['saving_tep'] = saving.get('tep')

            if 'isSimulated' in data:
                vals['is_simulated'] = bool(data.get('isSimulated'))
            if 'isElectric' in data:
                vals['is_electric'] = bool(data.get('isElectric'))

            # write trip
            trip.sudo().write(vals)

            # replace waypoints if provided
            if 'waypoints' in data:
                waypoints = data.get('waypoints') or []
                # remove old
                trip.waypoint_ids.sudo().unlink()
                wp_model = request.env['trip.location'].sudo()
                for wp in waypoints:
                    try:
                        wp_model.create({
                            'trip_id': trip.id,
                            'latitude': wp.get('latitude'),
                            'longitude': wp.get('longitude'),
                        })
                    except Exception:
                        _logger.warning('Skipping invalid waypoint payload: %s', wp)

            # replace advised evehicles if provided
            if 'evehicles' in data:
                evehicles = data.get('evehicles') or []
                trip.advised_evehicle_ids.sudo().unlink()
                ev_model = request.env['trip.advised_evehicle'].sudo()
                for ev in evehicles:
                    try:
                        ev_model.create({
                            'trip_id': trip.id,
                            'make': ev.get('make'),
                            'model': ev.get('model'),
                            'name': ev.get('name'),
                            'autonomy': ev.get('autonomy'),
                            'mileage_perc': ev.get('mileagePerc') or ev.get('mileage_perc'),
                            'advise_perc': ev.get('advisePerc') or ev.get('advise_perc'),
                        })
                    except Exception:
                        _logger.warning('Skipping invalid evehicle payload: %s', ev)

            return {
                'status': True,
                'message': 'Trip updated successfully',
                'trip': self._prepare_trip_data(trip)
            }

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.exception("Error updating trip %s: %s", trip_id, e)
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/trips/<int:trip_id>', type='json', auth='none', methods=['DELETE'], csrf=False)
    def delete_trip(self, trip_id, **kwargs):
        """Delete trip"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            trip = self._get_user_trip(user, trip_id)
            trip.sudo().unlink()
            return {'status': True, 'message': 'Trip deleted successfully'}

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except Exception as e:
            _logger.exception("Error deleting trip %s: %s", trip_id, e)
            return utils._error_response('INTERNAL_ERROR', str(e))
