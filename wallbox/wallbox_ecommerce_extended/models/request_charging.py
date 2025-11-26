# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import logging
from odoo import models, fields, api, Command, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class RequestCharging(models.Model):
    _name = 'request.charging'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Request Charging'
    _order = 'service_requested_date desc'

    # ==========================
    # Fields Definition
    # ==========================
    # Basic Information
    name = fields.Char(string='Reference', required=True, default='New', readonly=True)
    service_id = fields.Char(string='Service ID', copy=False, readonly=True)
    wallbox_serial_id = fields.Many2one('stock.lot.report', string='Wallbox Serial', domain=[("has_return", "=", False)], required=True)
    charging_station_id = fields.Many2one('charging.station', string='Charging Station', compute="_compute_charging_station_id", store=True)

    # Date/Time Information
    reservation_requested = fields.Boolean(string='Reservation Requested')
    reservation_date = fields.Datetime(string='Reservation Date')
    service_requested_date = fields.Datetime(string='Request Date', readonly=True, default=fields.Datetime.now)
    service_scheduled_date = fields.Datetime(string='Scheduled Date')
    service_completion_date = fields.Datetime(string='Completion Date', related="request_charging_session_id.end_time")

    # Charging Details
    charging_duration = fields.Float(string='Charging Duration (hours)')
    charging_power = fields.Float(string='Charging Power (kW)')
    energy_consumed = fields.Float(string='Energy Consumed (kWh)')

    # Financial Information
    payment_method = fields.Selection(
        selection=[
            ('cash', 'Cash or Manual'),
            ('pre-authorize', 'Pre-Authorize Transaction')
        ], string='Payment Method')
    sale_order_id = fields.Many2one('sale.order', string='Sale Order', readonly=True)
    payment_link = fields.Char(string='Payment Link', readonly=True)

    currency_id = fields.Many2one('res.currency', string='Currency', related="sale_order_id.currency_id")
    amount_total = fields.Monetary(string='Amount Total', related="sale_order_id.amount_total", store=True, currency_field='currency_id')
    amount_paid = fields.Float(string='Amount Paid', related="sale_order_id.amount_paid", store=True)

    # payment_status = fields.Selection(
    #     selection=[
    #         ('draft', 'Draft'),
    #         ('pending', 'Pending'),
    #         ('paid', 'Paid'),
    #         ('cancelled', 'Cancelled')
    #     ], string='Payment Status', default='draft', readonly=True)
    # authorized_transaction_ids = fields.Many2many('payment.transaction',
    #     string="Authorized Transactions",
    #     related="sale_order_id.authorized_transaction_ids")
    authorized_transaction_id = fields.Many2one(
        'payment.transaction',
        string='Payment Transaction',
        compute="_compute_authorized_transaction_id",
        store=True,
    )
    transaction_state = fields.Selection(related="authorized_transaction_id.state", store=True, string="Transaction State")

    @api.depends('sale_order_id.transaction_ids', 'sale_order_id.transaction_ids.state')
    def _compute_authorized_transaction_id(self):
        for rec in self:
            if rec.sale_order_id and rec.sale_order_id.transaction_ids:
                rec.authorized_transaction_id = rec.sale_order_id.transaction_ids[0]
                # rec.authorized_transaction_id = rec.sale_order_id.authorized_transaction_ids[0]
            else:
                rec.authorized_transaction_id = False

    # Status Information
    request_status = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('requested', 'Requested'),
            ('approved', 'Approved'),
            ('scheduled', 'Scheduled'),
            ('in_progress', 'In Progress'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled')
        ], 
        string='Request Status',
        default='draft', tracking=True)

    # Relationships
    wallbox_owner_id = fields.Many2one('res.partner', string='Wallbox Owner', compute="_compute_property_details", store=True)
    building_id = fields.Many2one('building.building', string='Building', compute="_compute_property_details", store=True)
    parking_space_id = fields.Many2one('parking.space', string='Parking Space', compute="_compute_property_details", store=True)
    condominium_id = fields.Many2one('condominium.condominium', string='Condominium', compute="_compute_property_details", store=True)
    wallbox_device_id = fields.Many2one('product.template', string='Wallbox Device',
        domain="[('is_wallbox_device', '=', True)]", compute="_compute_property_details", store=True)
    request_user_id = fields.Many2one('res.partner', string='Customer', required=True, readonly=True, default=lambda self: self.env.user.partner_id.id)
    vehicle_id = fields.Many2one('user.vehicle', string='Vehicle', required=True)

    # Additional Information
    service_notes = fields.Text(string='Service Notes')
    customer_confirmation = fields.Boolean(string='Customer Confirmation')
    documentation = fields.Binary(string='Documentation')
    documentation_filename = fields.Char(string='Documentation Filename')
    service_feedback = fields.Text(string='Service Feedback')
    rating = fields.Integer(string='Rating')
    request_charging_session_id = fields.Many2one('wallbox.charging.session', string='Requested Charging Session')

    # =====================================================
    # All Compute Flags for full charging request flow
    # =====================================================
    is_request_user = fields.Boolean(string='Is Requested User', compute="_compute_is_request_user")
    is_wallbox_owner = fields.Boolean(string='Is Wallbox Owner', compute="_compute_is_wallbox_owner")
    can_request_charging = fields.Boolean(string='Can Request Charging', compute="_compute_can_request_charging", store=True)
    can_start_charging = fields.Boolean(string='Can Start Charging', compute="_compute_can_start_charging", store=True)
    visible_payment_link_btn = fields.Boolean(string='Visible payment button', compute="_compute_visible_payment_link_btn", store=True)
    visible_schedule_charging_btn = fields.Boolean(string='Visible Schedule Charging button', compute="_compute_visible_schedule_charging_btn", store=True)
    is_guest_user_request = fields.Boolean(string='Is Guest User Request', compute="_compute_is_guest_user_request", store=True)

    @api.depends('request_user_id', 'wallbox_owner_id', 'charging_station_id')
    def _compute_is_guest_user_request(self):
        for request in self:
            if request.request_user_id == request.wallbox_owner_id or request.request_user_id.id in request.charging_station_id.allowed_partner_ids.ids:
                request.is_guest_user_request = False
            else:
                request.is_guest_user_request = True

    @api.depends('request_status', 'payment_link', 'transaction_state')
    def _compute_visible_payment_link_btn(self):
        for request in self:
            request.visible_payment_link_btn = True
            if not request.payment_link or request.request_status not in ('approved') or request.transaction_state:
                request.visible_payment_link_btn = False

    @api.depends('request_status', 'transaction_state', 'wallbox_serial_id', 'payment_method')
    def _compute_visible_schedule_charging_btn(self):
        for request in self:
            # Default to False
            request.visible_schedule_charging_btn = False

            # Case 1: Wallbox owner
            if request.request_user_id == request.wallbox_owner_id:
                request.visible_schedule_charging_btn = (request.request_status == 'draft')

            # Case 2: Monthly billing user
            elif request.request_user_id.id in request.charging_station_id.allowed_partner_ids.ids:
                request.visible_schedule_charging_btn = (request.request_status == 'draft')

            # Case 3: Guest user
            else:
                if request.payment_method == 'cash':
                    # For cash payments, just need approved status
                    request.visible_schedule_charging_btn = (request.request_status == 'approved')
                else:
                    # For pre-authorize payments, need approved status AND authorized transaction
                    request.visible_schedule_charging_btn = (
                        request.request_status == 'approved' and 
                        request.transaction_state != 'authorized'
                    )

    '''
    Cases: For display 'Request Charging' button
    - if 'wallbox owner' and 'requested customer' is same then can request charging = False
    - if not same , there are two cases (wallbox user(monthly billing), guest charging)
    - if wallbox user (monthly billing)
        - can request charging = False
    - if guest charging
        - can request charging = True
    '''
    @api.depends('request_user_id', 'wallbox_owner_id', 'request_status', 'charging_station_id.allowed_partner_ids')
    def _compute_can_request_charging(self):
        for request in self:
            # Default to False
            request.can_request_charging = False

            # Only in draft status can request charging
            if request.request_status != 'draft':
                continue

            # Must have a charging station
            if not request.charging_station_id:
                continue

            # Case 1: Request user is wallbox owner - cannot request charging (owner doesn't need to request)
            if request.request_user_id == request.wallbox_owner_id:
                continue

            # Case 2: Request user is in allowed partners (monthly billing user)
            if request.request_user_id.id in request.charging_station_id.allowed_partner_ids.ids:
                continue

            # Case 3: Guest charging - can request
            request.can_request_charging = True

    '''
    Cases: For display 'Start Charging' button
    - if 'wallbox owner' and 'requested customer' is same then can_start_charging = True
    - if not same , there are two cases (wallbox user(monthly billing), guest charging)
    - if wallbox user (monthly billing)
        - check SO only not 'authorize transaction'
        - request stage is in ('scheduled')
    - if guest charging
        - check SO and transaction state = authorized
        - request stage is in ('approved', 'scheduled')
    '''
    @api.depends('request_user_id', 'wallbox_owner_id', 'request_status', 
             'transaction_state', 'charging_station_id.allowed_partner_ids', 'sale_order_id')
    def _compute_can_start_charging(self):
        for request in self:
            # Default to False
            request.can_start_charging = False

            # Must be in approved or scheduled status
            if request.request_status not in ('approved', 'scheduled'):
                continue

            # Case 1: Request user is wallbox owner - can always start
            if request.request_user_id == request.wallbox_owner_id:
                request.can_start_charging = True
                continue

            # Case 2: Request user is in allowed partners (monthly billing user)
            if request.request_user_id.id in request.charging_station_id.allowed_partner_ids.ids:
                # Just need an existing sale order
                if request.sale_order_id:
                    request.can_start_charging = True
                continue

            # Case 3: Guest charging - need authorized transaction
            if request.authorized_transaction_id and request.transaction_state == "authorized":
                request.can_start_charging = True

    def _compute_is_request_user(self):
        active_partner = self.env.user.partner_id
        for rec in self:
            rec.is_request_user = True if rec.request_user_id == active_partner else False

    def _compute_is_wallbox_owner(self):
        active_partner = self.env.user.partner_id
        for rec in self:
            rec.is_wallbox_owner = True if rec.wallbox_owner_id == active_partner else False

    # =====================================================
    # END of all Flags method.
    # =====================================================

    @api.depends('wallbox_serial_id')
    def _compute_charging_station_id(self):
        for request in self:
            if request.wallbox_serial_id:
                ChargingStation = self.env['charging.station'].search([('charger_id', '=', request.wallbox_serial_id.lot_id.name)], limit=1)
                if ChargingStation:
                    request.charging_station_id = ChargingStation.id
                else:
                    request.charging_station_id = False
            else:
                request.charging_station_id = False

    @api.depends('wallbox_serial_id')
    def _compute_property_details(self):
        for request in self:
            if request.wallbox_serial_id:
                request.write({
                    'wallbox_device_id': request.wallbox_serial_id.product_id.product_tmpl_id.id,
                    'wallbox_owner_id': request.wallbox_serial_id.partner_id.parent_id.id or request.wallbox_serial_id.partner_id.id,
                    'parking_space_id': request.wallbox_serial_id.partner_id.parking_space_id.id,
                    'building_id': request.wallbox_serial_id.partner_id.building_id.id,
                    'condominium_id': request.wallbox_serial_id.partner_id.condominium_id.id
                })
            else:
                request.write({
                    'wallbox_device_id': False,
                    'wallbox_owner_id': False,
                    'parking_space_id': False,
                    'building_id': False,
                    'condominium_id': False
                })

    def action_authorized_transaction(self):
        return {
            'name': _("Authorize Transaction"),
            'type': 'ir.actions.act_url',
            'url': self.payment_link,
            'target': 'new',
        }

    # ==========================
    # Model Methods
    # ==========================

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('name') or vals['name'] == _('New'):
                vals['name'] = self.env['ir.sequence'].next_by_code('request.charging') or _('New')
        return super().create(vals_list)

    def action_request_charging(self):
        if self.request_user_id != self.env.user.partner_id:
            raise ValidationError("Only Current Requested User can request charging.")
        self.service_requested_date = fields.Datetime.now()
        self.request_status = 'requested'

    def action_approve(self):
        """Approve charging request with proper payment handling.

        Cases:
        - Only wallbox owner can approve requests
        - Approval is only needed for guest users (not in allowed_partner_ids)
        - Must be in 'requested' status
        - Handles two payment methods:
            1. Cash/Manual - Owner collects payment manually
            2. Pre-Authorize - System collects via pre-authorized transaction
        """
        for record in self:
            # Validate approval conditions
            self._validate_approval_conditions(record)

            # Create sale order for all cases
            record._create_charging_sale_order()

            # Handle payment method specific logic
            if record.payment_method == 'cash':
                record._handle_cash_payment()
            elif record.payment_method == 'pre-authorize':
                record._handle_preauthorize_payment()

            # Update status to approved
            record.request_status = 'approved'
        return True

    def _validate_approval_conditions(self, record):
        """Validate all conditions required for approval"""
        # Check if current user is the wallbox owner
        if record.wallbox_owner_id != self.env.user.partner_id:
            raise ValidationError("Only wallbox owner can approve charging requests.")

        # Check if the charging status is appropriate for approval
        if record.request_status != 'requested':
            raise ValidationError("Only requested charges can be approved.")

        # Ensure payment method is selected
        if not record.payment_method:
            raise ValidationError("""Payment method is required for Guest request:
                1. Cash - Collect payment manually
                2. Pre-Authorize - System collects via pre-authorized transaction""")

        # Verify this is actually a guest request needing approval
        if record.request_user_id.id in record.charging_station_id.allowed_partner_ids.ids:
            raise ValidationError("Monthly billing users don't need approval")

    def _create_charging_sale_order(self):
        """Create sale order for the charging request"""
        if not self.sale_order_id:  # Only create if doesn't exist
            product = self.env.ref('wallbox_ecommerce_extended.product_product_wallbox_charging')
            self.sale_order_id = self.env['sale.order'].sudo().create({
                'partner_id': self.request_user_id.id,
                'date_order': fields.Datetime.now(),
                'request_charging_id': self.id,
                'user_id': self.wallbox_owner_id.user_id.id or self.wallbox_owner_id.user_ids[0].id,
                'order_line': [Command.create({
                    'product_id': product.id,
                    'price_unit': self.charging_station_id.guest_max_amount_limit,
                    'product_uom_qty': 1,
                })],
            })
            # Send Notification on mobile app for sale order created.
            notification_model = self.env['push.notification'].sudo()
            success = notification_model.send_expo_notification(self.request_user_id.user_id or self.request_user_id.user_ids[0], 'Sale order is created for your charging request.')

    def _handle_cash_payment(self):
        """Handle cash payment specific logic"""
        self._send_notification(
            "Your charging request has been approved. Please pay in cash to the wallbox owner.",
            self.request_user_id
        )

    def _handle_preauthorize_payment(self):
        """Handle pre-authorize payment specific logic"""
        # Generate payment link
        payment_link_wizard = self.env['payment.link.wizard'].sudo().with_context(
            active_model='sale.order',
            active_id=self.sale_order_id.id
        ).create(self.sale_order_id._get_default_payment_link_values())

        self.payment_link = payment_link_wizard.link

        self._send_notification(
            "Your charging request has been approved. Please complete payment using this link: %s" % self.payment_link,
            self.request_user_id
        )

    def action_schedule_charging(self):
        if self.request_user_id != self.wallbox_owner_id and self.request_user_id.id not in self.charging_station_id.sudo().allowed_partner_ids.ids and self.request_status in ['draft', 'requested']:
            raise ValidationError(_("Guest User Must require an approval for charging."))
        if not self.service_scheduled_date:
            raise ValidationError(_("Scheduled date is required for schedule the charging."))
        self._create_charging_sale_order()
        self.request_status = 'scheduled'

    def _send_notification(self, message, recipient):
        """Helper method to send notifications"""
        self.env['mail.message'].create({
            'body': message,
            'subject': 'Charging Request Update',
            'partner_ids': [(6, 0, [recipient.id])],
            'model': self._name,
            'res_id': self.id,
        })

    # Cases : for start charging
    # If owner self charging (requested_user_id and wallbox_owner_id is same)
        # - request_status must be in scheduled
        # - only requested_user_id can start the charging
        # - check for the sale order is created and linked
    # If wallbox user charging (requested_user_id and wallbox_owner_id is not same and requested_user_id in charging_station_id.allowed_partner_ids)
        # - request_status must be in scheduled
        # - only requested_user_id can start the charging
        # - check for the sale order is created and linked
    # If Guest User Charging (requested_user_id and wallbox_owner_id is not same and requested_user_id not in charging_station_id.allowed_partner_ids)
        # - request_status must be in (scheduled, approved)
        # - only requested_user_id can start the charging
        # - check for the sale order is created and linked
        # - check the authorized_transaction_id is set
        # - check the transaction_state = 'authorized'
    # - when click on start charging it will send one request to CMS server for start transaction.
    # - CMS server will create one record of session and send us session record.
    # - we will create that session in odoo linked with current request charging station.
    # - after successfully session created and linked we will move request_status to 'In Progress'.

    def action_start_charging(self):
        """Handle starting charging session with validation for different user types
        Cases:
        1. Owner self charging:
           - request_status must be 'scheduled'
           - only requested_user_id can start
           - must have sale order

        2. Wallbox user charging (monthly billing):
           - request_status must be 'scheduled' 
           - only requested_user_id can start
           - must have sale order

        3. Guest user charging:
           - request_status must be in ('approved', 'scheduled')
           - only requested_user_id can start
           - must have sale order
           - must have authorized transaction
        """
        for record in self:
            record = record.sudo()
            # Common validations for all cases
            if record.request_user_id != self.env.user.partner_id:
                raise ValidationError(_("Only the requesting user can start charging."))

            if not record.sale_order_id:
                raise ValidationError(_("Sale order is required to start charging."))

            if not record.charging_station_id or not record.charging_station_id.charger_id:
                raise ValidationError(_("Charging station not properly configured with CSMS ID."))

            # Case-specific validations
            if record.request_user_id == record.wallbox_owner_id:
                # Case 1: Owner self charging
                if record.request_status != 'scheduled':
                    raise ValidationError(_("Owner charging must be scheduled before starting."))

            elif record.request_user_id.id in record.charging_station_id.allowed_partner_ids.ids:
                # Case 2: Wallbox user (monthly billing)
                if record.request_status != 'scheduled':
                    raise ValidationError(_("Monthly billing user charging must be scheduled before starting."))

            else:
                # Case 3: Guest user charging
                if record.request_status not in ('approved', 'scheduled'):
                    raise ValidationError(_("Guest charging must be approved or scheduled before starting."))

                if not record.authorized_transaction_id or record.transaction_state != 'authorized':
                    raise ValidationError(_("Authorized payment transaction is required for guest charging."))

            # All validations passed - proceed with starting charging
            try:
                max_amount_limit = 0
                if record.request_user_id != record.wallbox_owner_id or record.request_user_id.id not in record.charging_station_id.allowed_partner_ids.ids:
                    # max_amount_limit = record.sale_order_id.amount_total
                    max_amount_limit = record.charging_station_id.guest_max_amount_limit

                # Call remote start API
                cms_api = self.env['csms.api']
                response = cms_api.remote_start_transaction(
                    charger_id=record.charging_station_id.charger_id,
                    customer_id=record.request_user_id.id,
                    max_limit=max_amount_limit,
                    charging_power_limit=record.charging_power,
                    odoo_request_id=record.id,
                )

                # Check response - either dict with success or other response format
                if isinstance(response, dict) and response.get('success'):
                    # Update request status
                    record.request_status = 'in_progress'
                # else:
                #     # Handle other response formats if needed
                #     record.request_status = 'in_progress'
                return response

            except Exception as e:
                _logger.error(f"Failed to start charging: {str(e)}")
                raise UserError(_("Failed to start charging: %s") % str(e))

    def action_complete_charging(self):
        """Handle completion of charging session including CMS API integration"""
        for record in self:
            # Validate charging can be completed
            if record.request_status != 'in_progress':
                raise ValidationError(_("Only in-progress charges can be completed."))

            if record.request_user_id != self.env.user.partner_id:
                raise ValidationError(_("Only the requesting user can complete charging."))

            try:
                # Get the active charging session
                session = record.request_charging_session_id
                if session.status in ('Ended', 'Failed'):
                    raise ValidationError(_("No active charging session found to complete"))

                # Call remote stop API if we have a transaction ID
                if session.transaction_id:
                    cms_api = self.env['csms.api']
                    response = cms_api.remote_stop_transaction(
                        charger_id=record.charging_station_id.charger_id,
                        transaction_id=session.transaction_id
                    )

                    # Send completion notification
                    record._send_notification(
                        _("Your charging session has been completed successfully"),
                        record.request_user_id
                    )

                    return response

            except Exception as e:
                _logger.error(f"Failed to complete charging session: {str(e)}")
                raise UserError(_("Failed to complete charging session: %s") % str(e))

    def action_cancel(self):
        for record in self:
            if record.wallbox_owner_id != self.env.user.partner_id:
                raise ValidationError("Only wallbox owner can Cancel request charging request.")
            if record.request_status in ['completed', 'cancelled']:
                raise ValidationError("Cannot cancel already completed or cancelled charges.")
            record.request_status = 'cancelled'
            # TODO: Send cancellation notification

    # ==========================
    # Constraints
    # ==========================
    @api.constrains('service_scheduled_date', 'service_requested_date')
    def _check_dates(self):
        for record in self:
            if (record.is_guest_user_request and record.service_scheduled_date and 
                record.service_scheduled_date < record.service_requested_date):
                raise ValidationError("Scheduled date cannot be before request date.")

    def write(self, vals):
        # First call the original write method
        res = super(RequestCharging, self).write(vals)

        # Check if request_status is being updated to 'completed'
        if 'request_status' in vals and vals['request_status'] == 'completed':
            for record in self:
                # Only proceed if we have a charging station with charger_id
                if record.charging_station_id and record.charging_station_id.charger_id:
                    try:
                        # Call unlock connector API
                        cms_api = self.env['csms.api']
                        cms_api.unlock_connector(
                            charger_id=record.charging_station_id.charger_id
                        )
                        _logger.info(
                            "Successfully unlocked connector for charger %s (Request: %s)",
                            record.charging_station_id.charger_id,
                            record.name
                        )
                    except Exception as e:
                        _logger.error(
                            "Failed to unlock connector for charger %s (Request: %s): %s",
                            record.charging_station_id.charger_id,
                            record.name,
                            str(e)
                        )
                        # Continue without raising to avoid blocking the status change
        return res

    def unlink(self):
        for request in self:
            if request.request_status not in ('draft'):
                raise ValidationError("You can not delete the charging request which is not in draft stage.")
        return super().unlink()

    def _get_prepared_charging_request_data(self):
        """Prepare charging request data with direct fields and M2O names"""
        self.ensure_one()

        data = {
            # Basic Fields
            'id': self.id,
            'name': self.name,
            'request_status': self.request_status,

            # Dates
            'reservation_requested': self.reservation_requested,
            'reservation_date': str(self.reservation_date),
            'service_requested_date': str(self.service_requested_date),
            'service_scheduled_date': str(self.service_scheduled_date),

            # Charging Details
            'charging_duration': self.charging_duration,
            'charging_power': self.charging_power,
            'energy_consumed': self.energy_consumed,
            'request_charging_session_id': self.request_charging_session_id.sudo().transaction_id if self.request_charging_session_id else None,

            # Payment & Status
            'payment_method': self.payment_method,
            'payment_link': self.payment_link,
            'transaction_state': self.transaction_state,
            'amount_total': self.amount_total,
            'sale_order_id': self.sale_order_id.name if self.sale_order_id else None,

            # M2O Fields (with names)
            'wallbox_serial_id': {
                'id': self.wallbox_serial_id.id,
                'name': self.wallbox_serial_id.lot_id.name,
            },
            'request_user_id': {
                'id': self.request_user_id.id,
                'name': self.request_user_id.name,
            },
            'vehicle_id': {
                'id': self.vehicle_id.sudo().id,
                'name': self.vehicle_id.sudo().name,
            },
            'charging_station_id': {
                'id': self.charging_station_id.sudo().id,
                'name': self.charging_station_id.sudo().name,
                'status': self.charging_station_id.status,
            } if self.charging_station_id else None,

            # Optional Fields
            'service_notes': self.service_notes,
            'customer_confirmation': self.customer_confirmation,
            'service_feedback': self.service_feedback,
            'rating': self.rating,

            # Flags
            'can_request_charging': self.can_request_charging,
            'can_start_charging': self.can_start_charging,
            'visible_payment_link_btn': self.visible_payment_link_btn,
            'visible_schedule_charging_btn': self.visible_schedule_charging_btn,
            'is_guest_user_request': self.is_guest_user_request,
        }

        return data
