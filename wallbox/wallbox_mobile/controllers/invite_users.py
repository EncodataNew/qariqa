# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
import json
from odoo import http
from odoo.http import request, Response
from odoo.addons.wallbox_mobile import utils
from werkzeug.exceptions import Unauthorized
from odoo.addons.web.controllers.utils import ensure_db

_logger = logging.getLogger(__name__)


class WallboxSharingController(http.Controller):

    def _json_response(self, data, status=200):
        """Helper method to return JSON responses"""
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    def _validate_wallbox_access(self, user, wallbox_id):
        """Validate user has permission to manage this wallbox"""
        wallbox = request.env['charging.station'].with_user(user).browse(wallbox_id)
        if not wallbox.exists():
            return None, self._json_response(
                utils._error_response('NOT_FOUND', 'Wallbox not found'),
                404
            )
        
        if wallbox.owner_id != user.partner_id:
            return None, self._json_response(
                utils._error_response('ACCESS_DENIED', 'Only owners/admins can manage invitations'),
                403
            )

        return wallbox, None

    # ----------------------------------------
    # POST /v1/wallboxes/{id}/invitations
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations', 
                type='http', auth='none', methods=['POST'], csrf=False)
    def create_invitation(self, wallbox_id, **kwargs):
        print(">>>>>> self", self)
        print(">>>>>>>>> wallbox_id", wallbox_id)
        print(">>>>>>>>>>> kwargs", kwargs)
        """Add partner to allowed users and send invitation"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            print(">>>>>>>>>>>> user", user)
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            # Validate wallbox access
            print(">>>>>> validation")
            wallbox, error_response = self._validate_wallbox_access(user, wallbox_id)
            if error_response:
                return error_response
            print(">>>>>> validation kkkkkk")
            # Parse input
            try:
                data = json.loads(request.httprequest.data)
                partner_email = data.get('email')
                if not partner_email:
                    raise ValueError("Email is required")
            except Exception as e:
                return self._json_response(
                    utils._error_response('INVALID_DATA', str(e)),
                    400
                )

            # Find or create partner
            print(">>>>>>>> partner_email", partner_email)
            partner = request.env['res.partner'].sudo().search([('email', '=', partner_email)], limit=1)
            print(">>>>>>>>>>>>> partner1", partner)
            print(">>>>>>>>>>> company_id", user.company_id.id)
            if not partner:
                partner = request.env['res.partner'].sudo().create({
                    'name': data.get('name', partner_email),
                    'email': partner_email,
                    'phone': data.get('phone'),
                    'is_wallbox_user': True,
                    'company_id': user.company_id.id,
                })
            print(">>>>>>>>>>>>> partner2", partner)

            # Add to allowed partners if not already present
            if partner.id not in wallbox.allowed_partner_ids.ids:
                wallbox.sudo().write({
                    'allowed_partner_ids': [(4, partner.id)]
                })
                print("<<>>>>>>>>>>>> successfully ddoe")
                # Send invitation
                partner.sudo().invite_wallbox_user()

            return self._json_response({
                'status': True,
                'message': 'Invitation sent successfully',
                'data': {
                    'invite_id': partner.id,  # Using partner ID as invite ID
                    'email': partner.email,
                    'name': partner.name,
                    'status': 'pending'
                }
            })

        except Exception as e:
            _logger.error("Error creating invitation: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    # ----------------------------------------
    # GET /v1/wallboxes/{id}/invitations
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations', 
                type='http', auth='none', methods=['GET'], csrf=False)
    def list_invitations(self, wallbox_id, **kwargs):
        """List all allowed partners (invitations)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            wallbox, error_response = self._validate_wallbox_access(user, wallbox_id)
            if error_response:
                return error_response

            invitations = []
            for partner in wallbox.allowed_partner_ids:
                invitations.append({
                    'invite_id': partner.id,
                    'email': partner.email,
                    'name': partner.name,
                    'status': 'active',  # Simplified status since we're not tracking separately
                    'access_type': 'monthly'  # Default for allowed_partner_ids
                })

            return self._json_response({
                'status': True,
                'data': invitations,
                'count': len(invitations)
            })

        except Exception as e:
            _logger.error("Error listing invitations: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    # ----------------------------------------
    # PUT /v1/wallboxes/{id}/invitations/{inviteId}
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations/<int:invite_id>', 
                type='http', auth='none', methods=['PUT'], csrf=False)
    def update_invitation(self, wallbox_id, invite_id, **kwargs):
        """Update partner details (name, email, etc.)"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            wallbox, error_response = self._validate_wallbox_access(user, wallbox_id)
            if error_response:
                return error_response

            # Verify partner is in allowed list
            partner = request.env['res.partner'].browse(invite_id)
            if partner.id not in wallbox.allowed_partner_ids.ids:
                return self._json_response(
                    utils._error_response('NOT_FOUND', 'Invitation not found for this wallbox'),
                    404
                )

            # Update partner details
            try:
                data = json.loads(request.httprequest.data)
                update_vals = {}
                if 'name' in data:
                    update_vals['name'] = data['name']
                if 'phone' in data:
                    update_vals['phone'] = data['phone']
                
                if update_vals:
                    partner.write(update_vals)

                return self._json_response({
                    'status': True,
                    'message': 'Invitation updated successfully',
                    'data': {
                        'invite_id': partner.id,
                        'email': partner.email,
                        'name': partner.name
                    }
                })

            except Exception as e:
                return self._json_response(
                    utils._error_response('INVALID_DATA', str(e)),
                    400
                )

        except Exception as e:
            _logger.error("Error updating invitation: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    # ----------------------------------------
    # DELETE /v1/wallboxes/{id}/invitations/{inviteId}
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations/<int:invite_id>', 
                type='http', auth='none', methods=['DELETE'], csrf=False)
    def delete_invitation(self, wallbox_id, invite_id, **kwargs):
        """Remove partner from allowed users"""
        ensure_db()
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            wallbox, error_response = self._validate_wallbox_access(user, wallbox_id)
            if error_response:
                return error_response

            # Remove partner from allowed list
            wallbox.write({
                'allowed_partner_ids': [(3, invite_id)]
            })

            return self._json_response({
                'status': True,
                'message': 'Invitation removed successfully',
                'data': {
                    'invite_id': invite_id
                }
            })

        except Exception as e:
            _logger.error("Error deleting invitation: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', str(e)),
                500
            )

    # ----------------------------------------
    # POST /v1/wallboxes/{id}/invitations/{inviteId}/accept
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations/<int:invite_id>/accept', 
                type='http', auth='none', methods=['POST'], csrf=False)
    def accept_invitation(self, wallbox_id, invite_id, **kwargs):
        """Endpoint for invited user to accept (handled in frontend)"""
        return self._json_response({
            'status': True,
            'message': 'Invitation accepted',
            'data': {
                'invite_id': invite_id,
                'wallbox_id': wallbox_id
            }
        })

    # ----------------------------------------
    # POST /v1/wallboxes/{id}/invitations/{inviteId}/reject
    # ----------------------------------------
    @http.route('/v1/wallboxes/<int:wallbox_id>/invitations/<int:invite_id>/reject', 
                type='http', auth='none', methods=['POST'], csrf=False)
    def reject_invitation(self, wallbox_id, invite_id, **kwargs):
        """Endpoint for invited user to reject (handled in frontend)"""
        return self._json_response({
            'status': True,
            'message': 'Invitation rejected',
            'data': {
                'invite_id': invite_id,
                'wallbox_id': wallbox_id
            }
        })
