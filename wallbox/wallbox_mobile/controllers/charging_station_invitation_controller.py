# -*- coding: utf-8 -*-
import json
import logging
from odoo import http
from odoo.http import request, Response
from odoo.addons.wallbox_mobile import utils
from odoo.exceptions import ValidationError, UserError
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class ChargingStationInvitationController(http.Controller):

    def _json_response(self, data, status=200):
        return Response(
            json.dumps(data),
            status=status,
            mimetype='application/json'
        )

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++++++++++SEND INVITATIONS ENDPOINTS+++++++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # ++++++++++++++++++++++++++++++++++++++
    # + Create Send Invitation
    # ++++++++++++++++++++++++++++++++++++++

    @http.route('/v1/invitation', type='json', auth='user', methods=['POST'], csrf=False)
    def create_invitation(self, **kwargs):
        """Create invitation in draft status - don't send automatically"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            charging_station_id = data.get('charging_station_id')
            if not charging_station_id:
                return utils._error_response('VALIDATION_ERROR', 'Charging Station ID is required', user=user)

            charging_station = request.env['charging.station'].browse(charging_station_id)
            if not charging_station.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Charging Station not found', user=user)
            
            if charging_station.owner_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'You are not the owner of this charging station', user=user)

            receiver_id = data.get('receiver_id')
            user_name = data.get('user_name')
            email = data.get('email')
            mobile = data.get('mobile')

            if receiver_id:
                receiver = request.env['res.partner'].browse(receiver_id)
                if not receiver.exists():
                    return utils._error_response('RESOURCE_NOT_FOUND', 'Receiver ID is invalid - user not found', user=user)
                
                invitation_vals = {
                    'request_type': 'owner_to_user',
                    'charging_station_id': charging_station_id,
                    'sender_id': user.partner_id.id,
                    'receiver_id': receiver_id,
                    'user_name': receiver.name,
                    'email': receiver.email,
                    'mobile': receiver.mobile or receiver.phone,
                    'note': data.get('note', ''),
                    'status': 'draft'
                }

            elif user_name and email and mobile:
                existing_receiver = request.env['res.partner'].search([
                    ('email', '=', email)
                ], limit=1)

                if existing_receiver:
                    invitation_vals = {
                        'request_type': 'owner_to_user',
                        'charging_station_id': charging_station_id,
                        'sender_id': user.partner_id.id,
                        'receiver_id': existing_receiver.id,
                        'user_name': existing_receiver.name,
                        'email': existing_receiver.email,
                        'mobile': existing_receiver.mobile or existing_receiver.phone,
                        'note': data.get('note', ''),
                        'status': 'draft'
                    }
                else:
                    invitation_model = request.env['charging.station.invitation']
                    new_receiver_id = invitation_model.create_partner_user(
                        name=user_name, 
                        email=email, 
                        mobile=mobile
                    )
                    
                    invitation_vals = {
                        'request_type': 'owner_to_user',
                        'charging_station_id': charging_station_id,
                        'sender_id': user.partner_id.id,
                        'receiver_id': new_receiver_id,
                        'user_name': user_name,
                        'email': email,
                        'mobile': mobile,
                        'note': data.get('note', ''),
                        'status': 'draft'
                    }

            else:
                return utils._error_response('VALIDATION_ERROR', 'Either provide Receiver ID OR provide User Name, Email and Mobile', user=user)

            invitation = request.env['charging.station.invitation'].create(invitation_vals)
            
            result = {
                'success': True, 
                'message': 'Invitation created successfully in draft',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status,
                'charging_station': charging_station.name,
                'receiver_name': invitation.user_name,
                'receiver_email': invitation.email
            }

            utils._log_api_error(api_name="/v1/invitation", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error creating invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # +++++++++++++++++++++++++++++++++++++
    # + Get Send Invitation Records Only
    # +++++++++++++++++++++++++++++++++++++

    @http.route('/v1/invitation', type='http', auth='user', methods=['GET'], csrf=False)
    def get_invitation(self, **kwargs):
        """Get only Send Invitation records (owner_to_user) for current user"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            invitations = request.env['charging.station.invitation'].search([
                ('request_type', '=', 'owner_to_user')
            ], order="create_date desc")

            data = []
            for invitation in invitations:
                data.append({
                    'id': invitation.id,
                    'name': invitation.name,
                    'charging_station_id': invitation.charging_station_id.sudo().id,
                    'charging_station_name': invitation.charging_station_id.sudo().name,
                    'sender_id': invitation.sender_id.id,
                    'sender_name': invitation.sender_id.name,
                    'receiver_id': invitation.receiver_id.id,
                    'receiver_name': invitation.receiver_id.name,
                    'user_name': invitation.user_name,
                    'email': invitation.email,
                    'mobile': invitation.mobile,
                    'request_type': invitation.request_type,
                    'status': invitation.status,
                    'note': invitation.note,
                    'create_date': invitation.create_date.strftime('%Y-%m-%d %H:%M:%S') if invitation.create_date else '',
                })

            result = {
                'success': True,
                'send_invitations': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/invitation", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching send invitations: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user),
                500
            )

    # ++++++++++++++++++
    # + Send Invitation
    # ++++++++++++++++++

    @http.route('/v1/invitation/send', type='json', auth='user', methods=['POST'], csrf=False)
    def send_invitation(self, **kwargs):
        """Send invitation using invitation_id"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Invitation not found', user=user)

            if invitation.request_type != 'owner_to_user':
                return utils._error_response('VALIDATION_ERROR', 'This is not send invitation record', user=user)

            if invitation.sender_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only sender can send the invitation', user=user)

            if invitation.status != 'draft':
                return utils._error_response('VALIDATION_ERROR', 'Only draft invitations can be sent', user=user)

            invitation.action_send_invitation()

            result = {
                'success': True,
                'message': 'Invitation sent successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/send", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error sending invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # ++++++++++++++++++
    # + Accept Invitation
    # ++++++++++++++++++

    @http.route('/v1/invitation/accept', type='json', auth='user', methods=['POST'], csrf=False)
    def accept_invitation(self, **kwargs):
        """Accept invitation using invitation_id - ONLY for send type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Invitation not found', user=user)

            if invitation.request_type != 'owner_to_user':
                return utils._error_response('VALIDATION_ERROR', 'This endpoint is only for Send Invitations. Use /v1/invitation/accept_request for Request Invitations.', user=user)

            if invitation.receiver_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only receiver can accept the invitation', user=user)

            if invitation.status != 'pending':
                return utils._error_response('VALIDATION_ERROR', 'Only pending invitations can be accepted', user=user)

            invitation.action_accept_invitation()

            result = {
                'success': True,
                'message': 'Invitation accepted successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/accept", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error accepting invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # ++++++++++++++++++
    # + Reject Invitation
    # ++++++++++++++++++

    @http.route('/v1/invitation/reject', type='json', auth='user', methods=['POST'], csrf=False)
    def reject_invitation(self, **kwargs):
        """Reject invitation using invitation_id - ONLY for send type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Invitation not found', user=user)

            if invitation.request_type != 'owner_to_user':
                return utils._error_response('VALIDATION_ERROR', 'This endpoint is only for Send Invitations. Use /v1/invitation/reject_request for Request Invitations.', user=user)

            if invitation.receiver_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only receiver can reject the invitation', user=user)

            if invitation.status != 'pending':
                return utils._error_response('VALIDATION_ERROR', 'Only pending invitations can be rejected', user=user)

            invitation.action_reject_invitation()

            result = {
                'success': True,
                'message': 'Invitation rejected successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/reject", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error rejecting invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++              END                      ++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++REQUEST  INVITATION ENDPOINTS++++++++++++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # ++++++++++++++++++++++++
    # + Create Request Invitation
    # ++++++++++++++++++++++++

    @http.route('/v1/invitation/request', type='json', auth='user', methods=['POST'], csrf=False)
    def create_request_invitation(self, **kwargs):
        """Create request invitation in draft status"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            charging_station_name = data.get('charging_station_name')
            if not charging_station_name:
                return utils._error_response('VALIDATION_ERROR', 'Charging Station Name is required', user=user)

            invitation_vals = {
                'request_type': 'user_to_owner',
                'charging_station_name': charging_station_name,
                'sender_id': user.partner_id.id,
                'note': data.get('note', ''),
                'status': 'draft'
            }

            invitation = request.env['charging.station.invitation'].create(invitation_vals)
            
            result = {
                'success': True, 
                'message': 'Request invitation created successfully in draft',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status,
                'charging_station_name': charging_station_name
            }

            utils._log_api_error(api_name="/v1/invitation/request", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error creating request invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # +++++++++++++++++++++++++++++++++++++
    # + Get Request Invitation Records Only
    # +++++++++++++++++++++++++++++++++++++

    @http.route('/v1/invitation/request', type='http', auth='user', methods=['GET'], csrf=False)
    def get_request_invitations(self, **kwargs):
        """Get only Request Invitation records (user_to_owner) for current user"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return self._json_response(user, 401)

            invitations = request.env['charging.station.invitation'].search([
                ('request_type', '=', 'user_to_owner'),
            ], order="create_date desc")

            data = []
            for invitation in invitations:
                data.append({
                    'id': invitation.id,
                    'name': invitation.name,
                    'charging_station_id': invitation.charging_station_id.sudo().id,
                    'charging_station_name': invitation.charging_station_id.sudo().name,
                    'sender_id': invitation.sender_id.id,
                    'sender_name': invitation.sender_id.name,
                    'receiver_id': invitation.receiver_id.id,
                    'receiver_name': invitation.receiver_id.name,
                    'request_type': invitation.request_type,
                    'status': invitation.status,
                    'note': invitation.note,
                    'is_sender': invitation.sender_id.id == user.partner_id.id,
                    'is_receiver': invitation.receiver_id.id == user.partner_id.id,
                    'create_date': invitation.create_date.strftime('%Y-%m-%d %H:%M:%S') if invitation.create_date else '',
                })

            result = {
                'success': True,
                'request_invitations': data,
                'count': len(data)
            }

            utils._log_api_error(api_name="/v1/invitation/request", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return self._json_response(result)

        except Exception as e:
            _logger.error("Error fetching request invitations: %s", str(e))
            return self._json_response(
                utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user),
                500
            )

    # ++++++++++++++++++++++++
    # + Request Invitation
    # ++++++++++++++++++++++++

    @http.route('/v1/invitation/request_invitation', type='json', auth='user', methods=['POST'], csrf=False)
    def request_invitation(self, **kwargs):
        """Request invitation using invitation_id - ONLY for request type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Request Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Request invitation not found', user=user)

            if invitation.request_type != 'user_to_owner':
                return utils._error_response('VALIDATION_ERROR', 'This is not request record', user=user)

            if invitation.sender_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only sender can request', user=user)

            if invitation.status != 'draft':
                return utils._error_response('VALIDATION_ERROR', 'Only draft invitations can be requested', user=user)

            invitation.action_invitation_request()

            result = {
                'success': True,
                'message': 'Invitation requested successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/request_invitation", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error requesting invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # ++++++++++++++++++++++++
    # + Accept Request
    # ++++++++++++++++++++++++

    @http.route('/v1/invitation/accept_request', type='json', auth='user', methods=['POST'], csrf=False)
    def accept_request(self, **kwargs):
        """Accept request invitation using invitation_id - ONLY for request type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Request Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Request invitation not found', user=user)

            if invitation.request_type != 'user_to_owner':
                return utils._error_response('VALIDATION_ERROR', 'This endpoint is only for Request Invitations. Use /v1/invitation/accept for Send Invitations.', user=user)

            if invitation.receiver_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only charging station owner can accept the request', user=user)

            if invitation.status != 'pending':
                return utils._error_response('VALIDATION_ERROR', 'Only pending request invitations can be accepted', user=user)

            invitation.action_accept_request()

            result = {
                'success': True,
                'message': 'Request invitation accepted successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/accept_request", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error accepting invitation request: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # ++++++++++++++++++++++++
    # + Reject Request
    # ++++++++++++++++++++++++

    @http.route('/v1/invitation/reject_request', type='json', auth='user', methods=['POST'], csrf=False)
    def reject_request(self, **kwargs):
        """Reject request invitation using invitation_id - ONLY for request type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Request Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Request invitation not found', user=user)

            if invitation.request_type != 'user_to_owner':
                return utils._error_response('VALIDATION_ERROR', 'This endpoint is only for Request Invitations. Use /v1/invitation/reject for Send Invitations.', user=user)

            if invitation.receiver_id != user.partner_id:
                return utils._error_response('AUTHORIZATION_ERROR', 'Only charging station owner can reject the request', user=user)

            if invitation.status != 'pending':
                return utils._error_response('VALIDATION_ERROR', 'Only pending request invitations can be rejected', user=user)

            invitation.action_reject_request()

            result = {
                'success': True,
                'message': 'Request invitation rejected successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/reject_request", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error rejecting invitation request: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++              END                      ++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    # ++++++++++++++++++
    # + Cancel Invitation
    # ++++++++++++++++++

    @http.route('/v1/invitation/cancel', type='json', auth='user', methods=['POST'], csrf=False)
    def cancel(self, **kwargs):
        """Cancel invitation using invitation_id - for both send and request type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Invitation not found', user=user)

            if invitation.request_type == 'owner_to_user':
                if invitation.sender_id != user.partner_id and invitation.receiver_id != user.partner_id:
                    return utils._error_response('AUTHORIZATION_ERROR', 'Only sender or receiver can cancel send invitations', user=user)
            elif invitation.request_type == 'user_to_owner':
                if invitation.sender_id != user.partner_id and invitation.receiver_id != user.partner_id:
                    return utils._error_response('AUTHORIZATION_ERROR', 'Only sender or receiver can cancel request invitations', user=user)
            else:
                return utils._error_response('VALIDATION_ERROR', 'Invalid invitation type', user=user)

            if invitation.status not in ['pending', 'accepted']:
                return utils._error_response('VALIDATION_ERROR', 'Only pending or accepted invitations can be cancelled', user=user)

            invitation.action_cancel()

            result = {
                'success': True,
                'message': 'Invitation cancelled successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/cancel", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error cancelling invitation: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # ++++++++++++++++++
    # + Reset to Draft
    # ++++++++++++++++++

    @http.route('/v1/invitation/reset_to_draft', type='json', auth='user', methods=['POST'], csrf=False)
    def reset_to_draft(self, **kwargs):
        """Reset invitation to draft using invitation_id - for both send and request type invitations"""
        try:
            user = utils._get_user_and_validate_request_authentication()
            if isinstance(user, dict) and user.get('error'):
                return user

            data = json.loads(request.httprequest.data)
            
            invitation_id = data.get('invitation_id')
            if not invitation_id:
                return utils._error_response('VALIDATION_ERROR', 'Invitation ID is required', user=user)

            invitation = request.env['charging.station.invitation'].browse(invitation_id)
            if not invitation.exists():
                return utils._error_response('RESOURCE_NOT_FOUND', 'Invitation not found', user=user)

            if invitation.request_type == 'owner_to_user':
                if invitation.sender_id != user.partner_id:
                    return utils._error_response('AUTHORIZATION_ERROR', 'Only sender can reset send invitations to draft', user=user)
            elif invitation.request_type == 'user_to_owner':
                if invitation.sender_id != user.partner_id:
                    return utils._error_response('AUTHORIZATION_ERROR', 'Only sender can reset request invitations to draft', user=user)
            else:
                return utils._error_response('VALIDATION_ERROR', 'Invalid invitation type', user=user)

            if invitation.status not in ['cancelled', 'rejected']:
                return utils._error_response('VALIDATION_ERROR', 'Only cancelled or rejected invitations can be reset to draft', user=user)

            invitation.action_reset_to_draft()

            result = {
                'success': True,
                'message': 'Invitation reset to draft successfully',
                'invitation_id': invitation.id,
                'invitation_name': invitation.name,
                'status': invitation.status
            }

            utils._log_api_error(api_name="/v1/invitation/reset_to_draft", error_code="SUCCESS", error_description="No Error", json_parameters=result, user=user)
            return result

        except ValidationError as e:
            return utils._error_response('VALIDATION_ERROR', str(e), user=user)
        except Exception as e:
            _logger.error("Error resetting invitation to draft: %s", str(e))
            return utils._error_response('INTERNAL_ERROR', 'Internal server error', user=user)

    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++++++++++++++              END                      ++++++++++++++++++++++++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++