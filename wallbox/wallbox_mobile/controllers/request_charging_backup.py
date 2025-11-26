
# # -*- coding: utf-8 -*-
# from odoo import http
# from odoo.http import request
# from odoo.addons.wallbox_mobile import utils
# from odoo.addons.web.controllers.utils import ensure_db
# from odoo.exceptions import ValidationError, AccessError
# import logging
# import json

# _logger = logging.getLogger(__name__)

# class ChargingRequestController(http.Controller):

#     # ============================================
#     # CHARGING REQUEST CREATION ENDPOINTS
#     # ============================================

#     @http.route('/v1/charging/requests/create', type='json', auth='none', methods=['POST'], csrf=False)
#     def create_charging_request(self, **post):
#         """
#         Create charging request endpoint
#         ---
#         tags: [Charging Requests]
#         summary: Create a new charging request
#         description: |
#           Creates a new charging request with different flows:
#           1. Owner charging - direct to scheduled
#           2. Monthly user - direct to scheduled
#           3. Guest user - goes to requested state
#         requestBody:
#           required: true
#           content:
#             application/json:
#               schema:
#                 type: object
#                 properties:
#                   wallbox_serial_id:
#                     type: string
#                     description: Serial number of the wallbox
#                     example: "WBX123456"
#                   vehicle_id:
#                     type: integer
#                     description: ID of the vehicle to charge
#                     example: 42
#                   service_scheduled_date:
#                     type: string
#                     format: date-time
#                     description: Required for owners/monthly users
#                     example: "2025-06-20 14:00:00"
#                 required: [wallbox_serial_id, vehicle_id]
#         responses:
#           '201':
#             description: Charging request created
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     request_id:
#                       type: integer
#                       example: 123
#                     request_status:
#                       type: string
#                       enum: [draft, requested, approved, scheduled, in_progress, completed, cancelled]
#                       example: "scheduled"
#                     next_action:
#                       type: string
#                       enum: [schedule, approval]
#                       example: "schedule"
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Missing required fields"
#                     code:
#                       type: integer
#                       example: 400
#           '401':
#             $ref: '#/components/responses/Unauthorized'
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Wallbox not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Parse and validate input
#             try:
#                 data = json.loads(request.httprequest.data)
#                 wallbox_serial = data.get('wallbox_serial_id')
#                 vehicle_id = data.get('vehicle_id')
#                 scheduled_date = data.get('service_scheduled_date')

#                 if not wallbox_serial or not vehicle_id:
#                     return {
#                         'status': False,
#                         'error': 'Wallbox serial and vehicle ID are required',
#                         'code': 400
#                     }

#             except ValueError:
#                 return {
#                     'status': False,
#                     'error': 'Invalid request data',
#                     'code': 400
#                 }

#             # 2. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'User authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 3. Validate wallbox
#             try:
#                 charging_station = request.env['charging.station'].sudo().search([
#                     ('serial_number', '=', wallbox_serial)
#                 ], limit=1)

#                 if not charging_station:
#                     return {
#                         'status': False,
#                         'error': 'Wallbox not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Wallbox lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Wallbox validation failed',
#                     'code': 500
#                 }

#             # 4. Check user permissions
#             try:
#                 is_owner = (user.partner_id == charging_station.owner_id)
#                 is_monthly_user = (user.partner_id.id in charging_station.allowed_partner_ids.ids)

#                 if (is_owner or is_monthly_user) and not scheduled_date:
#                     return {
#                         'status': False,
#                         'error': 'Scheduled date is required for owners/monthly users',
#                         'code': 400
#                     }
#             except Exception as e:
#                 _logger.error("Permission check error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 5. Create request
#             try:
#                 vals = {
#                     'wallbox_serial_id': charging_station.id,
#                     'vehicle_id': vehicle_id, 



#                     'request_user_id': user.partner_id.id,
#                     'request_status': 'scheduled' if (is_owner or is_monthly_user) else 'requested'
#                 }

#                 if is_owner or is_monthly_user:
#                     vals['service_scheduled_date'] = scheduled_date

#                 charging_request = request.env['request.charging'].sudo().create(vals)

#                 return {
#                     'status': True,
#                     'request_id': charging_request.id,
#                     'request_status': charging_request.request_status,
#                     'next_action': 'schedule' if (is_owner or is_monthly_user) else 'approval'
#                 }

#             except Exception as e:
#                 _logger.error("Request creation failed: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Failed to create charging request',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in charging request: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Charging request service unavailable',
#                 'code': 500
#             }

#     # ============================================
#     # APPROVAL FLOW ENDPOINTS (FOR WALLBOX OWNERS)
#     # ============================================

#     @http.route('/v1/charging/requests/<int:request_id>/request', type='json', auth='none', methods=['POST'], csrf=False)
#     def request_charging(self, request_id, **post):
#         """
#         Submit charging request for approval
#         ---
#         tags: [Charging Requests]
#         summary: Submit charging request for approval
#         description: |
#           Submits a charging request for approval (guest users only).
#           Validates:
#           1. Request is in draft status
#           2. User is guest (not owner/monthly user)
#           3. User is the requester
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         responses:
#           '200':
#             description: Request submitted successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     request_status:
#                       type: string
#                       example: "requested"
#                     message:
#                       type: string
#                       example: "Request submitted for approval"
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Only draft requests can be submitted"
#                     code:
#                       type: integer
#                       example: 400
#           '403':
#             description: Forbidden
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Not authorized to submit this request"
#                     code:
#                       type: integer
#                       example: 403
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'Authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 2. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             # 3. Validate user permissions
#             try:
#                 # Check if user is the requester
#                 if user.partner_id != charging_request.request_user_id:
#                     return {
#                         'status': False,
#                         'error': 'Only requesting user can submit for approval',
#                         'code': 403
#                     }

#                 # Check if request is in draft status
#                 if charging_request.request_status != 'draft':
#                     return {
#                         'status': False,
#                         'error': 'Only draft requests can be submitted for approval',
#                         'code': 400
#                     }

#                 # Check if user is guest (not owner/monthly user)
#                 charging_station = charging_request.charging_station_id
#                 if (user.partner_id == charging_station.owner_id or 
#                     user.partner_id.id in charging_station.allowed_partner_ids.ids):
#                     return {
#                         'status': False,
#                         'error': 'Owners and monthly users don\'t need approval',
#                         'code': 400
#                     }
#             except Exception as perm_error:
#                 _logger.error("Permission check error: %s", str(perm_error))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 4. Process the request
#             try:
#                 charging_request.with_user(user).action_request_charging()

#                 # Notify wallbox owner
#                 if charging_station.owner_id:
#                     try:
#                         charging_request._send_notification(
#                             "New charging request awaiting your approval",
#                             charging_station.owner_id
#                         )
#                     except Exception as notify_error:
#                         _logger.warning("Notification failed: %s", str(notify_error))

#                 return {
#                     'status': True,
#                     'request_status': charging_request.request_status,
#                     'message': 'Request submitted for approval'
#                 }

#             except Exception as process_error:
#                 _logger.error("Request processing failed: %s", str(process_error))
#                 return {
#                     'status': False,
#                     'error': 'Failed to submit request',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in request submission: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Request submission service unavailable',
#                 'code': 500
#             }

#     # @http.route('/v1/charging/requests/<int:request_id>/approve', type='json', auth='none', methods=['POST'], csrf=False)
#     # def approve_charging_request(self, request_id, **post):
#     #     """
#     #     Approve a charging request (wallbox owner only)
#     #     """
#     #     ensure_db()
#     #     try:
#     #         data = json.loads(request.httprequest.data)
#     #         user = request.env['res.users'].sudo().browse(request.session.uid)
#     #         charging_request = request.env['request.charging'].sudo().browse(request_id)

#     #         if not charging_request.exists():
#     #             raise ValidationError("Charging request not found")

#     #         # Validate owner
#     #         if user.partner_id != charging_request.wallbox_owner_id:
#     #             raise AccessError("Only wallbox owner can approve requests")
#     #         charging_request.with_user(user).action_approve()

#     #         # # Handle payment link generation for pre-auth
#     #         response_data = {
#     #             'request_status': charging_request.request_status,
#     #             'payment_method': charging_request.payment_method,
#     #             'payment_link': charging_request.payment_link,
#     #             'amount_total': charging_request.amount_total,
#     #             'sale_order_id': charging_request.sale_order_id.name,
#     #         }

#     #         return {
#     #             'status': 'success',
#     #             'data': response_data
#     #         }

#     #     except Exception as e:
#     #         _logger.error("Error approving charging request: %s", str(e))
#     #         return {
#     #             'status': 'error',
#     #             'error': str(e)
#     #         }

#     @http.route('/v1/charging/requests/<int:request_id>/approve', type='json', auth='none', methods=['POST'], csrf=False)
#     def approve_charging_request(self, request_id, **post):
#         """
#         Approve charging request
#         ---
#         tags: [Charging Requests]
#         summary: Approve charging request
#         description: |
#           Approves a charging request (wallbox owner only).
#           Requires payment method in request body.
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         requestBody:
#           required: true
#           content:
#             application/json:
#               schema:
#                 type: object
#                 properties:
#                   payment_method:
#                     type: string
#                     enum: [cash, pre-authorize]
#                     description: Payment method for charging session
#                 required: [payment_method]
#         responses:
#           '200':
#             description: Request approved successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     data:
#                       type: object
#                       properties:
#                         request_status:
#                           type: string
#                           example: "approved"
#                         payment_method:
#                           type: string
#                           example: "pre-authorize"
#                         payment_link:
#                           type: string
#                           example: "https://payment.link/123"
#                         amount_total:
#                           type: number
#                           example: 15.75
#                         sale_order_id:
#                           type: string
#                           example: "SO1234"
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Payment method is required"
#                     code:
#                       type: integer
#                       example: 400
#           '403':
#             description: Forbidden
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Only wallbox owner can approve requests"
#                     code:
#                       type: integer
#                       example: 403
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Parse and validate input
#             try:
#                 data = json.loads(request.httprequest.data)
#                 payment_method = data.get('payment_method', '').strip().lower()
                
#                 if not payment_method or payment_method not in ['cash', 'pre-authorize']:
#                     return {
#                         'status': False,
#                         'error': 'Valid payment method is required (cash or pre-authorize)',
#                         'code': 400
#                     }
#             except ValueError:
#                 return {
#                     'status': False,
#                     'error': 'Invalid request data',
#                     'code': 400
#                 }

#             # 2. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'Authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 3. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             # 4. Validate owner permissions
#             try:
#                 if user.partner_id != charging_request.wallbox_owner_id:
#                     return {
#                         'status': False,
#                         'error': 'Only wallbox owner can approve requests',
#                         'code': 403
#                     }
#             except Exception as perm_error:
#                 _logger.error("Permission check error: %s", str(perm_error))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 5. Process approval
#             try:
#                 # Set payment method before approval
#                 charging_request.write({'payment_method': payment_method})
#                 charging_request.with_user(user).action_approve()

#                 response_data = {
#                     'request_status': charging_request.request_status,
#                     'payment_method': charging_request.payment_method,
#                     'payment_link': charging_request.payment_link,
#                     'amount_total': charging_request.amount_total,
#                     'sale_order_id': charging_request.sale_order_id.name if charging_request.sale_order_id else None,
#                 }

#                 return {
#                     'status': True,
#                     'data': response_data
#                 }

#             except Exception as process_error:
#                 _logger.error("Approval processing failed: %s", str(process_error))
#                 return {
#                     'status': False,
#                     'error': 'Failed to approve request',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in request approval: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Request approval service unavailable',
#                 'code': 500
#             }

#     # ============================================
#     # SCHEDULING ENDPOINTS
#     # ============================================

#     # @http.route('/v1/charging/requests/<int:request_id>/schedule', type='json', auth='none', methods=['POST'], csrf=False)
#     # def schedule_charging(self, request_id, **post):
#     #     """
#     #     Schedule a charging session
#     #     Flow:
#     #     1. For owners/monthly users - directly schedules charging
#     #     2. For guest users - requires approved status and proper payment
#     #     3. Validates scheduled date is provided
#     #     4. Creates sale order if needed
#     #     """
#     #     ensure_db()
#     #     try:
#     #         data = json.loads(request.httprequest.data)
#     #         user = request.env['res.users'].sudo().browse(request.session.uid)
#     #         charging_request = request.env['request.charging'].sudo().browse(request_id)

#     #         if not charging_request.exists():
#     #             raise ValidationError("Charging request not found")

#     #         # Validate scheduled date is provided
#     #         if 'service_scheduled_date' not in data:
#     #             raise ValidationError("Scheduled date is required")

#     #         # Validate user can schedule
#     #         if user.partner_id != charging_request.request_user_id:
#     #             raise AccessError("Only requesting user can schedule charging")

#     #         # Prepare values for update
#     #         vals = {
#     #             'service_scheduled_date': data['service_scheduled_date']
#     #         }

#     #         # Additional validation for guest users
#     #         if (charging_request.request_user_id != charging_request.wallbox_owner_id and 
#     #             charging_request.request_user_id.id not in charging_request.charging_station_id.allowed_partner_ids.ids):

#     #             # Guest users must be approved first
#     #             if charging_request.request_status != 'approved':
#     #                 raise ValidationError("Guest users must be approved before scheduling")

#     #             # For pre-authorize payments, transaction must be authorized
#     #             if (charging_request.payment_method == 'pre-authorize' and 
#     #                 charging_request.transaction_state != 'authorized'):
#     #                 raise ValidationError("Payment must be authorized before scheduling")

#     #         # Update the scheduled date first
#     #         charging_request.write(vals)

#     #         # Call the schedule action method
#     #         charging_request.with_user(user).action_schedule_charging()

#     #         return {
#     #             'status': 'success',
#     #             'request_status': charging_request.request_status,
#     #             'scheduled_date': charging_request.service_scheduled_date,
#     #             'sale_order_id': charging_request.sale_order_id.name if charging_request.sale_order_id else None,
#     #             'payment_status': charging_request.transaction_state
#     #         }

#     #     except Exception as e:
#     #         _logger.error("Error scheduling charging: %s", str(e))
#     #         return {
#     #             'status': 'error',
#     #             'error': str(e)
#     #         }

#     @http.route('/v1/charging/requests/<int:request_id>/schedule', type='json', auth='none', methods=['POST'], csrf=False)
#     def schedule_charging(self, request_id, **post):
#         """
#         Schedule charging session
#         ---
#         tags: [Charging Requests]
#         summary: Schedule charging session
#         description: |
#           Schedules a charging session after validation:
#           1. For owners/monthly users - directly schedules
#           2. For guest users - requires approved status and proper payment
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         requestBody:
#           required: true
#           content:
#             application/json:
#               schema:
#                 type: object
#                 properties:
#                   service_scheduled_date:
#                     type: string
#                     format: date-time
#                     description: Scheduled date/time for charging
#                     example: "2025-06-20 14:00:00"
#                 required: [service_scheduled_date]
#         responses:
#           '200':
#             description: Charging scheduled successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     request_status:
#                       type: string
#                       example: "scheduled"
#                     scheduled_date:
#                       type: string
#                       format: date-time
#                       example: "2025-06-20 14:00:00"
#                     sale_order_id:
#                       type: string
#                       example: "SO1234"
#                     payment_status:
#                       type: string
#                       example: "authorized"
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Scheduled date is required"
#                     code:
#                       type: integer
#                       example: 400
#           '403':
#             description: Forbidden
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Payment must be authorized before scheduling"
#                     code:
#                       type: integer
#                       example: 403
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Parse and validate input
#             try:
#                 data = json.loads(request.httprequest.data)
#                 scheduled_date = data.get('service_scheduled_date')
                
#                 if not scheduled_date:
#                     return {
#                         'status': False,
#                         'error': 'Scheduled date is required',
#                         'code': 400
#                     }
#             except ValueError:
#                 return {
#                     'status': False,
#                     'error': 'Invalid request data',
#                     'code': 400
#                 }

#             # 2. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'Authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 3. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             # 4. Validate user permissions
#             try:
#                 if user.partner_id != charging_request.request_user_id:
#                     return {
#                         'status': False,
#                         'error': 'Only requesting user can schedule charging',
#                         'code': 403
#                     }
#             except Exception as perm_error:
#                 _logger.error("Permission check error: %s", str(perm_error))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 5. Validate guest user requirements
#             try:
#                 is_guest = (user.partner_id != charging_request.wallbox_owner_id and 
#                            user.partner_id.id not in charging_request.charging_station_id.allowed_partner_ids.ids)
                
#                 if is_guest:
#                     if charging_request.request_status != 'approved':
#                         return {
#                             'status': False,
#                             'error': 'Guest users must be approved before scheduling',
#                             'code': 403
#                         }
                    
#                     if (charging_request.payment_method == 'pre-authorize' and 
#                         charging_request.transaction_state != 'authorized'):
#                         return {
#                             'status': False,
#                             'error': 'Payment must be authorized before scheduling',
#                             'code': 403
#                         }
#             except Exception as validation_error:
#                 _logger.error("Guest validation error: %s", str(validation_error))
#                 return {
#                     'status': False,
#                     'error': 'Guest validation failed',
#                     'code': 500
#                 }

#             # 6. Process scheduling
#             try:
#                 vals = {
#                     'service_scheduled_date': scheduled_date
#                 }
#                 charging_request.write(vals)
#                 charging_request.with_user(user).action_schedule_charging()

#                 return {
#                     'status': True,
#                     'request_status': charging_request.request_status,
#                     'scheduled_date': charging_request.service_scheduled_date,
#                     'sale_order_id': charging_request.sale_order_id.name if charging_request.sale_order_id else None,
#                     'payment_status': charging_request.transaction_state
#                 }

#             except Exception as process_error:
#                 _logger.error("Scheduling processing failed: %s", str(process_error))
#                 return {
#                     'status': False,
#                     'error': 'Failed to schedule charging',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in scheduling: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Scheduling service unavailable',
#                 'code': 500
#             }

#     # ============================================
#     # CHARGING SESSION CONTROL ENDPOINTS
#     # ============================================

#     # @http.route('/v1/charging/requests/<int:request_id>/start', type='json', auth='none', methods=['POST'], csrf=False)
#     # def start_charging(self, request_id, **post):
#     #     """
#     #     Start a charging session
#     #     """
#     #     ensure_db()
#     #     try:
#     #         user = request.env['res.users'].sudo().browse(request.session.uid)
#     #         charging_request = request.env['request.charging'].sudo().browse(request_id)

#     #         if not charging_request.exists():
#     #             raise ValidationError("Charging request not found")

#     #         # Validate user can start
#     #         if user.partner_id != charging_request.request_user_id:
#     #             raise AccessError("Only requesting user can start charging")

#     #         response = charging_request.with_user(user).action_start_charging()

#     #         # print(">>>>>>>>>>>>> response", response)

#     #         return {
#     #             'status': 'success',
#     #             'response': response,
#     #             'request_status': charging_request.request_status,
#     #             'session_id': charging_request.request_charging_session_id.id if charging_request.request_charging_session_id else None
#     #         }

#     #     except Exception as e:
#     #         _logger.error("Error starting charging: %s", str(e))
#     #         return {
#     #             'status': 'error',
#     #             'error': str(e)
#     #         }

#     @http.route('/v1/charging/requests/<int:request_id>/start', type='json', auth='none', methods=['POST'], csrf=False)
#     def start_charging(self, request_id, **post):
#         """
#         Start charging session
#         ---
#         tags: [Charging Requests]
#         summary: Start charging session
#         description: |
#           Starts a charging session after validation:
#           1. Request must be in scheduled status
#           2. Only requesting user can start
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         responses:
#           '200':
#             description: Charging started successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     request_status:
#                       type: string
#                       example: "in_progress"
#                     session_id:
#                       type: integer
#                       example: 123
#                     meter_start:
#                       type: number
#                       example: 0.0
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Cannot start charging - request not in scheduled status"
#                     code:
#                       type: integer
#                       example: 400
#           '403':
#             description: Forbidden
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Only requesting user can start charging"
#                     code:
#                       type: integer
#                       example: 403
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'Authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 2. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             # 3. Validate user permissions
#             try:
#                 if user.partner_id != charging_request.request_user_id:
#                     return {
#                         'status': False,
#                         'error': 'Only requesting user can start charging',
#                         'code': 403
#                     }
#             except Exception as perm_error:
#                 _logger.error("Permission check error: %s", str(perm_error))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 4. Validate request status
#             try:
#                 if charging_request.request_status != 'scheduled':
#                     return {
#                         'status': False,
#                         'error': 'Cannot start charging - request not in scheduled status',
#                         'code': 400
#                     }
#             except Exception as status_error:
#                 _logger.error("Status validation error: %s", str(status_error))
#                 return {
#                     'status': False,
#                     'error': 'Status validation failed',
#                     'code': 500
#                 }

#             # 5. Start charging session
#             try:
#                 result = charging_request.with_user(user).action_start_charging()

#                 # Get meter reading if available
#                 # meter_start = 0.0
#                 # if charging_request.request_charging_session_id:
#                 #     meter_start = charging_request.request_charging_session_id.meter_start or 0.0

#                 return {
#                     'status': True,
#                     'request_status': charging_request.request_status,
#                     'session_id': charging_request.request_charging_session_id.id if charging_request.request_charging_session_id else None,
#                     # 'meter_start': meter_start
#                 }

#             except Exception as process_error:
#                 _logger.error("Charging start failed: %s", str(process_error))
#                 return {
#                     'status': False,
#                     'error': 'Failed to start charging session',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in charging start: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Charging start service unavailable',
#                 'code': 500
#             }

#     # @http.route('/v1/charging/requests/<int:request_id>/complete', type='json', auth='none', methods=['POST'], csrf=False)
#     # def complete_charging(self, request_id, **post):
#     #     """
#     #     Complete a charging session
#     #     """
#     #     ensure_db()
#     #     try:
#     #         user = request.env['res.users'].sudo().browse(request.session.uid)
#     #         charging_request = request.env['request.charging'].sudo().browse(request_id)

#     #         if not charging_request.exists():
#     #             raise ValidationError("Charging request not found")

#     #         # Validate user can complete
#     #         if user.partner_id != charging_request.request_user_id:
#     #             raise AccessError("Only requesting user can complete charging")

#     #         charging_request.with_user(user).action_complete_charging()

#     #         return {
#     #             'status': 'success',
#     #             'request_status': charging_request.request_status,
#     #             'energy_consumed': charging_request.energy_consumed,
#     #             'amount_charged': charging_request.amount_total
#     #         }

#     #     except Exception as e:
#     #         _logger.error("Error completing charging: %s", str(e))
#     #         return {
#     #             'status': 'error',
#     #             'error': str(e)
#     #         }

#     @http.route('/v1/charging/requests/<int:request_id>/complete', type='json', auth='none', methods=['POST'], csrf=False)
#     def complete_charging(self, request_id, **post):
#         """
#         Complete charging session
#         ---
#         tags: [Charging Requests]
#         summary: Complete charging session
#         description: |
#           Completes a charging session after validation:
#           1. Request must be in progress
#           2. Only requesting user can complete
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         responses:
#           '200':
#             description: Charging completed successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     request_status:
#                       type: string
#                       example: "completed"
#                     energy_consumed:
#                       type: number
#                       description: Energy consumed in kWh
#                       example: 15.5
#                     amount_charged:
#                       type: number
#                       description: Total amount charged
#                       example: 7.25
#                     duration_minutes:
#                       type: number
#                       description: Total charging duration in minutes
#                       example: 45
#           '400':
#             description: Bad request
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Cannot complete charging - request not in progress"
#                     code:
#                       type: integer
#                       example: 400
#           '403':
#             description: Forbidden
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Only requesting user can complete charging"
#                     code:
#                       type: integer
#                       example: 403
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Authenticate user
#             try:
#                 user = request.env['res.users'].sudo().browse(request.session.uid)
#                 if not user.exists():
#                     return {
#                         'status': False,
#                         'error': 'Authentication failed',
#                         'code': 401
#                     }
#             except Exception as auth_error:
#                 _logger.error("Authentication error: %s", str(auth_error))
#                 return {
#                     'status': False,
#                     'error': 'Authentication failed',
#                     'code': 401
#                 }

#             # 2. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             # 3. Validate user permissions
#             try:
#                 if user.partner_id != charging_request.request_user_id:
#                     return {
#                         'status': False,
#                         'error': 'Only requesting user can complete charging',
#                         'code': 403
#                     }
#             except Exception as perm_error:
#                 _logger.error("Permission check error: %s", str(perm_error))
#                 return {
#                     'status': False,
#                     'error': 'Permission validation failed',
#                     'code': 500
#                 }

#             # 4. Validate request status
#             try:
#                 if charging_request.request_status != 'in_progress':
#                     return {
#                         'status': False,
#                         'error': 'Cannot complete charging - request not in progress',
#                         'code': 400
#                     }
#             except Exception as status_error:
#                 _logger.error("Status validation error: %s", str(status_error))
#                 return {
#                     'status': False,
#                     'error': 'Status validation failed',
#                     'code': 500
#                 }

#             # 5. Complete charging session
#             try:
#                 charging_request.with_user(user).action_complete_charging()
                
#                 # Calculate duration if session exists
#                 duration = 0
#                 if charging_request.request_charging_session_id:
#                     duration = (charging_request.request_charging_session_id.end_time - 
#                                charging_request.request_charging_session_id.start_time).total_seconds() / 60

#                 return {
#                     'status': True,
#                     'request_status': charging_request.request_status,
#                     'energy_consumed': charging_request.energy_consumed or 0,
#                     'amount_charged': charging_request.amount_total or 0,
#                     'duration_minutes': round(duration, 2)
#                 }

#             except Exception as process_error:
#                 _logger.error("Charging completion failed: %s", str(process_error))
#                 return {
#                     'status': False,
#                     'error': 'Failed to complete charging session',
#                     'code': 500
#                 }

#         except Exception as e:
#             _logger.error("Unexpected error in charging completion: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Charging completion service unavailable',
#                 'code': 500
#             }

#     # ============================================
#     # STATUS CHECK ENDPOINTS
#     # ============================================

#     @http.route('/v1/charging/requests/<int:request_id>/status', type='json', auth='none', methods=['GET'], csrf=False)
#     def get_charging_status(self, request_id, **kwargs):
#         """
#         Get charging request status
#         ---
#         tags: [Charging Requests]
#         summary: Get charging request status
#         description: |
#           Returns current status and available actions for a charging request
#         parameters:
#           - name: request_id
#             in: path
#             required: true
#             schema:
#               type: integer
#             description: Charging request ID
#         responses:
#           '200':
#             description: Status retrieved successfully
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: true
#                     data:
#                       type: object
#                       properties:
#                         request_status:
#                           type: string
#                           enum: [draft, requested, approved, scheduled, in_progress, completed, cancelled]
#                           example: "in_progress"
#                         can_start:
#                           type: boolean
#                           example: false
#                         can_complete:
#                           type: boolean
#                           example: true
#                         energy_consumed:
#                           type: number
#                           example: 15.5
#                         duration:
#                           type: number
#                           example: 45
#                         payment_status:
#                           type: string
#                           example: "authorized"
#                         payment_link:
#                           type: string
#                           example: "https://payment.link/123"
#           '404':
#             description: Not found
#             content:
#               application/json:
#                 schema:
#                   type: object
#                   properties:
#                     status:
#                       type: boolean
#                       example: false
#                     error:
#                       type: string
#                       example: "Charging request not found"
#                     code:
#                       type: integer
#                       example: 404
#           '500':
#             $ref: '#/components/responses/ServerError'
#         """
#         ensure_db()
#         try:
#             # 1. Validate charging request exists
#             try:
#                 charging_request = request.env['request.charging'].sudo().browse(request_id)
#                 if not charging_request.exists():
#                     return {
#                         'status': False,
#                         'error': 'Charging request not found',
#                         'code': 404
#                     }
#             except Exception as e:
#                 _logger.error("Request lookup error: %s", str(e))
#                 return {
#                     'status': False,
#                     'error': 'Request validation failed',
#                     'code': 500
#                 }

#             return {
#                 'status': True,
#                 'data': {
#                     'request_status': charging_request.request_status,
#                     'can_start': charging_request.can_start_charging,
#                     'can_complete': charging_request.request_status == 'in_progress',
#                     'energy_consumed': charging_request.energy_consumed or 0,
#                     'payment_status': charging_request.transaction_state or 'pending',
#                     'payment_link': charging_request.payment_link if getattr(charging_request, 'visible_payment_link_btn', False) else None
#                 }
#             }

#         except Exception as e:
#             _logger.error("Error getting charging status: %s", str(e), exc_info=True)
#             return {
#                 'status': False,
#                 'error': 'Failed to retrieve charging status',
#                 'code': 500
#             }

#     # ============================================
#     # LISTING ENDPOINTS
#     # ============================================

#     @http.route('/v1/charging/requests/my-requests', type='json', auth='none', methods=['GET'], csrf=False)
#     def list_my_requests(self, **kwargs):
#         """
#         List all charging requests for current user
#         """
#         ensure_db()
#         try:
#             user = utils._get_user_and_validate_request_authentication()
#             # user = request.env['res.users'].sudo().browse(request.session.uid) # this is also working
#             domain = [('request_user_id', '=', user.partner_id.id)]
#             requests = request.env['request.charging'].sudo().search(domain, order="service_requested_date desc")

#             request_list = []
#             for req in requests:
#                 request_list.append({
#                     'id': req.id,
#                     'reference': req.name,
#                     'wallbox_name': req.wallbox_serial_id.lot_id.name,
#                     'request_date': req.service_requested_date,
#                     'scheduled_date': req.service_scheduled_date,
#                     'status': req.request_status,
#                     'energy_consumed': req.energy_consumed,
#                     'amount': req.amount_total
#                 })

#             return {
#                 'status': 'success',
#                 'requests': request_list
#             }

#         except Exception as e:
#             _logger.error("Error listing charging requests: %s", str(e))
#             return {
#                 'status': 'error',
#                 'error': str(e)
#             }

#     @http.route('/v1/charging/requests/other-requests', type='json', auth='none', methods=['GET'], csrf=False)
#     def list_other_requests(self, **kwargs):
#         """
#         List all charging requests for wallboxes owned by current user
#         """
#         ensure_db()
#         try:
#             user = request.env['res.users'].sudo().browse(request.session.uid)
#             domain = [('wallbox_owner_id', '=', user.partner_id.id)]
#             requests = request.env['request.charging'].sudo().search(domain, order="service_requested_date desc")

#             request_list = []
#             for req in requests:
#                 request_list.append({
#                     'id': req.id,
#                     'reference': req.name,
#                     'customer_name': req.request_user_id.name,
#                     'request_date': req.service_requested_date,
#                     'status': req.request_status,
#                     'payment_method': req.payment_method,
#                     'payment_status': req.transaction_state,
#                     'requires_approval': req.can_request_charging
#                 })

#             return {
#                 'status': 'success',
#                 'requests': request_list
#             }

#         except Exception as e:
#             _logger.error("Error listing other requests: %s", str(e))
#             return {
#                 'status': 'error',
#                 'error': str(e)
#             }
