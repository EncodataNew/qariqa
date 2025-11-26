# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError , ValidationError


class WallboxOrder(models.Model):
    _name = 'wallbox.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Wallbox Order Management'

    # Customer
    name = fields.Char(string='Order Reference', copy=False, readonly=True, index=True, default='New')
    customer_id = fields.Many2one('res.partner',string='Customer',domain=lambda self: self._get_customer_domain(), tracking=True)

    @api.model
    def _get_customer_domain(self):
        """Smart domain for customer_id field."""
        domain = [('is_wallbox_user', '=', True)]
        user_partner_id = self.env.user.partner_id.id

        if self.env.user.has_group('wallbox_integration.group_wallbox_admin'):
            return domain
        elif self.env.user.has_group('wallbox_integration.group_wallbox_user'):
            domain.append(('id', '=', user_partner_id))
            return domain
        return [('id', '=', -1)]

    owner_id = fields.Many2one('res.partner', string='Owner', tracking=True)
    condominium_id = fields.Many2one('condominium.condominium', string='Condominium', tracking=True)
    building_id = fields.Many2one('building.building', string='Building',domain="[('condominium_id', '=?', condominium_id)]", tracking=True)
    parking_space_id = fields.Many2one('parking.space', string='Parking Space',domain="[('building_id', '=?', building_id)]", tracking=True)
    charging_station_id = fields.Many2one('charging.station', string='Charging Station', help="Consider as a charger - as par ocpp", tracking=True)

    # General field
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ], string="Status", default='draft', tracking=True)

    # Wallbox (Product Details)
    product_id = fields.Many2one('product.template', domain=[('is_wallbox_device', '=', True)], string='Wallbox Type', required=True, tracking=True)

    service_id = fields.Many2one('service.management', string='Service')
    wallbox_features = fields.Text(string='Wallbox Features')
    warranty_period = fields.Selection([
        ('2_years', '2 Years'),
        ('5_years', '5 Years')
    ], string='Warranty Period', tracking=True)

    # Schedule Installation
    installation_id = fields.Many2one('wallbox.installation', string='Installation', copy=False)
    installation_state = fields.Selection(related="installation_id.state" ,tracking=True)
    installation_date = fields.Date(string='Installation Date', copy=False, tracking=True)

    # Other
    documentation = fields.Binary(string='Documentation')
    service_notes = fields.Text(string='Service Notes')
    can_complete = fields.Boolean(string='Can Complete', compute="compute_can_complete", store=True)

    @api.onchange('condominium_id')
    def _onchange_condominium_id(self):
        self.building_id = False
        self.parking_space_id = False

    @api.onchange('building_id')
    def _onchange_building(self):
        if self.building_id:
            self.condominium_id = self.building_id.condominium_id
            self.parking_space_id = False

    @api.onchange('parking_space_id')
    def _onchange_parking_space(self):
        if self.parking_space_id:
            self.building_id = self.parking_space_id.building_id

    @api.depends('state', 'installation_id.state')
    def compute_can_complete(self):
        for rec in self:
            if rec.state == 'scheduled' and rec.installation_id and rec.installation_id.state == 'completed':
                rec.can_complete = True
            else:
                rec.can_complete = False

    def action_confirm(self):
        self.ensure_one()
        if self.name == _('New'):
            self.name = self.env['ir.sequence'].next_by_code('wallbox.order') or _('New')
        self.state = 'confirmed'

    def action_cancel(self):
        self.state = 'cancelled'

    def action_schedule_installation(self):
        context = {
            'default_order_id': self.id,
            'default_customer_id': self.customer_id.id,
        }
        view_id = self.env.ref('wallbox_integration.view_wallbox_installation_form_wizard').id
        return {
            'name': _('Schedule Installation'),
            'res_model': 'wallbox.installation',
            'view_mode': 'form',
            'views': [[view_id, 'form']],
            'context': context,
            'target': 'new',
            'type': 'ir.actions.act_window',
        }

    def action_reset_to_draft(self):
        self.state = 'draft'

    def action_complete(self):
        self.ensure_one()
        if not self.charging_station_id:
            charging_station_vals = {
                'name': self.env['ir.sequence'].next_by_code('charging.station') or 'New',
                'installation_date': self.installation_date,
                'owner_id': self.owner_id.id,
                'wallbox_order_id': self.id,
            }
            charging_station = self.env['charging.station'].create(charging_station_vals)
            self.charging_station_id = charging_station.id
            self.installation_id.charging_station_id = charging_station.id

        self.state = "completed"

    def action_view_scheduled_installation(self):
        self.ensure_one()
        if not self.installation_id:
            raise UserError("No installation record found for this order.")

        return {
            'type': 'ir.actions.act_window',
            'name': 'Scheduled Installation',
            'res_model': 'wallbox.installation',
            'view_mode': 'form',
            'res_id': self.installation_id.id,
            'target': 'current',
        }
