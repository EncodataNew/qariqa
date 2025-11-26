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

class RFIDTagController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    @http.route('/v1/rfid-tags', type='http', auth='none', methods=['GET'], csrf=False)
    def list_rfid_tags(self, **kwargs):
        """List all RFID tags for authenticated user"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            domain = [('charging_station_id.owner_id', '=', user.partner_id.id)]
            tags = request.env['rfid.tag'].with_user(user).search(domain)

            tag_list = [self._prepare_tag_data(tag) for tag in tags]

            result = {
                'status': True,
                'rfid_tags': tag_list,
                'count': len(tag_list)
            }

            utils._log_api_error(api_name="/v1/rfid-tags", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except Exception as e:
            _logger.error("Error listing RFID tags: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    @http.route('/v1/rfid-tags', type='json', auth='none', methods=['POST'], csrf=False)
    def create_rfid_tag(self, **kwargs):
        """Create a new RFID tag"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)

            # Validate required fields
            required_fields = ['tag_id', 'charging_station_id']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                return utils._error_response('VALIDATION_ERROR', 
                    f'Missing required fields: {", ".join(missing_fields)}')

            # Verify charging station ownership
            station = request.env['charging.station'].with_user(user).browse(data['charging_station_id'])
            if not station.exists() or station.owner_id != user.partner_id:
                return utils._error_response('ACCESS_DENIED', 'Invalid charging station')

            tag_data = {
                'tag_id': data['tag_id'],
                'charging_station_id': data['charging_station_id'],
                'is_allowed': data.get('is_allowed', True)
            }

            tag = request.env['rfid.tag'].with_user(user).create(tag_data)

            result = {
                'status': True,
                'message': 'RFID tag created successfully',
                'rfid_tag': self._prepare_tag_data(tag)
            }

            utils._log_api_error(api_name="/v1/rfid-tags", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.error("Error creating RFID tag: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/rfid-tags/<int:tag_id>', type='http', auth='none', methods=['GET'], csrf=False)
    def get_rfid_tag(self, tag_id, **kwargs):
        """Get RFID tag details"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            tag = self._get_user_tag(user, tag_id)

            result = {
                'status': True,
                'rfid_tag': self._prepare_tag_data(tag)
            }

            utils._log_api_error(api_name="/v1/rfid-tags/<int:tag_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return self._json_response(result)

        except NotFound as e:
            return Response(
                json.dumps(utils._error_response('RESOURCE_NOT_FOUND', str(e))),
                status=404,
                mimetype='application/json'
            )
        except Exception as e:
            _logger.error("Error getting RFID tag %s: %s", tag_id, str(e))
            return Response(
                json.dumps(utils._error_response('INTERNAL_ERROR', str(e))),
                status=500,
                mimetype='application/json'
            )

    @http.route('/v1/rfid-tags/<int:tag_id>', type='json', auth='none', methods=['PUT'], csrf=False)
    def update_rfid_tag(self, tag_id, **kwargs):
        """Update RFID tag information"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            tag = self._get_user_tag(user, tag_id)
            data = json.loads(request.httprequest.data)

            update_data = {}
            if 'tag_id' in data:
                update_data['tag_id'] = data['tag_id']
            if 'is_allowed' in data:
                update_data['is_allowed'] = data['is_allowed']
            if 'charging_station_id' in data:
                # Verify new charging station ownership
                station = request.env['charging.station'].with_user(user).browse(data['charging_station_id'])
                if not station.exists() or station.owner_id != user.partner_id:
                    return utils._error_response('ACCESS_DENIED', 'Invalid charging station')
                update_data['charging_station_id'] = data['charging_station_id']

            tag.write(update_data)

            result = {
                'status': True,
                'message': 'RFID tag updated successfully',
                'rfid_tag': self._prepare_tag_data(tag)
            }

            utils._log_api_error(api_name="/v1/rfid-tags/<int:tag_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e))
        except Exception as e:
            _logger.error("Error updating RFID tag %s: %s", tag_id, str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    @http.route('/v1/rfid-tags/<int:tag_id>', type='json', auth='none', methods=['DELETE'], csrf=False)
    def delete_rfid_tag(self, tag_id, **kwargs):
        """Delete an RFID tag"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            tag = self._get_user_tag(user, tag_id)
            tag.unlink()

            result = {
                'status': True,
                'message': 'RFID tag deleted successfully'
            }

            utils._log_api_error(api_name="/v1/rfid-tags/<int:tag_id>", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)

            return result

        except NotFound as e:
            return utils._error_response('RESOURCE_NOT_FOUND', str(e))
        except Exception as e:
            _logger.error("Error deleting RFID tag %s: %s", tag_id, str(e))
            return utils._error_response('INTERNAL_ERROR', str(e))

    def _get_user_tag(self, user, tag_id):
        """Helper to get tag and verify ownership through charging station"""
        tag = request.env['rfid.tag'].sudo().search([
            ('id', '=', tag_id),
            ('charging_station_id.owner_id', '=', user.partner_id.id)
        ], limit=1)

        if not tag:
            raise NotFound('RFID tag not found or access denied')
        return tag

    def _prepare_tag_data(self, tag):
        """Standardize tag data format"""
        return {
            'id': tag.id,
            'tag_id': tag.tag_id,
            'is_allowed': tag.is_allowed,
            'charging_station_id': tag.charging_station_id.id,
            'charging_station_name': tag.charging_station_id.name
        }
