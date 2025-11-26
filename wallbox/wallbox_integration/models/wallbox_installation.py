# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class WallboxInstallation(models.Model):
    _name = 'wallbox.installation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wallbox Installation Management'
    _order = 'scheduled_installation_date desc'

    # ========== Identification Fields ==========
    name = fields.Char(
        string='Installation Reference',
        copy=False,
        readonly=True,
        index=True,
        default='New'
    )
    order_id = fields.Many2one(
        'wallbox.order',
        string='Wallbox Order',
        required=True,
        ondelete='restrict'
    )

    # ========== Location Information ==========
    customer_id = fields.Many2one(
        'res.partner',
        string='Customer',
        required=True,
        related="order_id.customer_id",
        store=True
    )
    condominium_id = fields.Many2one(
        'condominium.condominium',
        string='Condominium',
        related="order_id.condominium_id",
    )
    building_id = fields.Many2one(
        'building.building',
        string='Building',
        related="order_id.building_id"
    )
    parking_space_id = fields.Many2one(
        'parking.space',
        string='Parking Space',
        related="order_id.parking_space_id"
    )
    charging_station_id = fields.Many2one(
        'charging.station',
        string='Charging Station',
        readonly=True,
        help="Automatically created and linked when wallbox order is completed"
    )
    charger_id = fields.Char(string='Charger ID')

    # ========== Installation Team ==========
    installation_technician_id = fields.Many2one(
        'res.partner',
        string='Installation Technician',
        domain=[('is_technician', '=', True)],
        tracking=True
    )

    # ========== Scheduling Fields ==========
    reservation_requested = fields.Boolean(
        string='Reservation Requested',
        tracking=True
    )
    reservation_date = fields.Date(
        string='Reservation Date',
        tracking=True
    )
    requested_installation_date = fields.Date(
        string='Requested Installation Date',
        required=True,
        default=fields.Date.context_today,
        tracking=True,
        help='Date when admin requested installation scheduling'
    )
    scheduled_installation_date = fields.Datetime(
        string='Installation Start Date',
        tracking=True,
        help='Technician-scheduled installation start date and time'
    )
    actual_installation_date = fields.Datetime(
        string='Actual Installation Date',
        tracking=True,
        help="Actual completion date and time of installation"
    )
    installation_duration = fields.Char(
        string='Installation Duration',
        compute='_compute_installation_duration',
        store=True,
        help='Duration between scheduled and actual installation'
    )
    rescheduled_date = fields.Date(
        string='Rescheduled Date',
        tracking=True
    )

    # ========== Documentation Fields ==========
    service_notes = fields.Text(
        string='Service Notes',
        help='Technical notes about the installation process'
    )
    customer_confirmation = fields.Boolean(
        string='Customer Confirmation',
        tracking=True,
        help='Customer has confirmed the installation'
    )
    documentation = fields.Text(
        string='Documentation',
        help='Installation documentation and manuals'
    )
    warranty_period = fields.Selection(
        [
            ('1_year', '1 Year'),
            ('2_years', '2 Years')
        ],
        string='Warranty Period',
        tracking=True
    )

    # ========== Status Management ==========
    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        default='draft',
        tracking=True
    )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('wallbox.installation') or 'New'
        installations = super(WallboxInstallation, self).create(vals_list)
        for installation in installations:
            if installation.order_id:
                installation.order_id.write({
                    'installation_id': installation.id,
                    'state': 'scheduled'
                })
        return installations

    @api.depends('scheduled_installation_date', 'actual_installation_date')
    def _compute_installation_duration(self):
        for record in self:
            if record.scheduled_installation_date and record.actual_installation_date:
                duration = record.actual_installation_date - record.scheduled_installation_date
                record.installation_duration = self._format_duration(duration)
            else:
                record.installation_duration = 'N/A'

    def _format_duration(self, duration):
        """Helper method to format timedelta as human-readable string"""
        days = duration.days
        seconds = duration.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f'{days}d {hours}h {minutes}m'

    @api.constrains('scheduled_installation_date', 'actual_installation_date')
    def _check_dates(self):
        for record in self:
            if record.scheduled_installation_date and record.actual_installation_date:
                if record.actual_installation_date <= record.scheduled_installation_date:
                    raise ValidationError(
                        _("Actual installation must occur after scheduled installation")
                    )

    # ========== State Transition Methods ==========
    def action_confirm(self):
        self.ensure_one()
        if self.name == 'New':
            self.name = self.env['ir.sequence'].next_by_code('wallbox.installation') or 'New'
        self.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_schedule(self):
        self.ensure_one()
        if not self.scheduled_installation_date:
            raise UserError(_("Please set a scheduled installation date first"))
        self.state = 'scheduled'

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_complete(self):
        for record in self:
            if self.installation_technician_id != self.env.user.partner_id:
                raise UserError(_("Only assigned technician can 'complete' this request."))
            if not record.actual_installation_date:
                raise UserError(_("Actual installation date is required to complete"))
            if not record.charger_id:
                raise UserError(_("You must have to add charger id for complete this installation."))
            record.state = "completed"
            record.order_id.sudo().installation_date = record.actual_installation_date
