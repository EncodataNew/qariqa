# -*- coding: utf-8 -*-
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

class ChargingStationInvitation(models.Model):
    _name = 'charging.station.invitation'
    _description = 'Charging Station Invitation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    name = fields.Char(string='Invitation Reference', readonly=True, copy=False, tracking=True)

    charging_station_id = fields.Many2one('charging.station', string='Charging Station', domain=lambda self: [('owner_id', '=', self.env.user.partner_id.id)], tracking=True)
    charging_station_name = fields.Char(string='Charger ID', help="Enter charger ID for owner invitation", tracking=True)

    sender_id = fields.Many2one('res.partner', string='Sender', required=True, tracking=True, default=lambda self: self.env.user.partner_id.id)
    receiver_id = fields.Many2one('res.partner', string='Receiver', tracking=True)

    user_name = fields.Char(string='User Name')
    email = fields.Char(string='Email')
    mobile = fields.Char(string='Mobile')

    request_type = fields.Selection([
        ('owner_to_user', 'Send Invitation'),
        ('user_to_owner', 'Request Invitation')
    ], string='Invitation Type', required=True, default="owner_to_user", tracking=True)

    status = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired')
    ], string='Status', default='draft', tracking=True)

    note = fields.Text(string='Note / Message')

    # Flags
    is_sender = fields.Boolean(string='Is Sender', compute="_compute_is_sender_receiver")
    is_receiver = fields.Boolean(string='Is Receiver', compute="_compute_is_sender_receiver")

    @api.depends('sender_id', 'receiver_id')
    def _compute_is_sender_receiver(self):
        current_user_partner_id = self.env.user.partner_id
        for rec in self:
            rec.is_sender = rec.sender_id == current_user_partner_id
            rec.is_receiver = rec.receiver_id == current_user_partner_id

    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
    # + General Code for request invitations flow and send invitation flow
    # ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

    def unlink(self):
        for record in self:
            if record.status != 'draft':
                raise UserError(_("Only draft record can be deleted."))
        return super().unlink()

    def action_reset_to_draft(self):
        self.status = 'draft'

    def action_cancel(self):
        self.status = 'cancelled'
        self.charging_station_id.sudo().allowed_partner_ids = [(3, self.receiver_id.id)]

    def create_partner_user(self, name, email, mobile=None):
        partner_id = self.env['res.partner'].sudo().create({
            'name': name,
            'email': email,
            'mobile': mobile,
            'is_wallbox_user': True,
        })
        # return partner_id
        partner_id.with_context(is_wallbox_user=True).invite_wallbox_user()
        return partner_id.id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('request_type') == 'user_to_owner':
                charging_station_id = self.env['charging.station'].sudo().search([
                    ('charger_id', '=', vals.get('charging_station_name'))
                ], limit=1)

                if charging_station_id:
                    vals['charging_station_id'] = charging_station_id.id
                    vals['receiver_id'] = charging_station_id.owner_id.id
                else:
                    raise ValidationError(_("Charger ID '%s' not found. Please check the Charger ID.") % vals.get('charging_station_name'))

            if vals.get('request_type') == 'owner_to_user':
                if not vals.get('charging_station_id'):
                    raise ValidationError(_("Charging Station is required to invite the user."))

                if not vals.get('receiver_id') and not vals.get('email'):
                    raise ValidationError(_("Receiver Id OR Email is required for send invitation."))

                if vals.get('email') and not vals.get('receiver_id'):
                    partner_id = self.env['res.partner'].sudo().search([
                        ('email', '=', vals.get('email'))
                    ], limit=1)

                    if partner_id:
                        vals['receiver_id'] = partner_id.id
                    elif not vals.get('mobile') or not vals.get('user_name'):
                        raise ValidationError(_("Please Add User Name and Mobile for create a user in the system."))

        return super().create(vals_list)

    # +++++++++++++++++++++++++++++++++++++
    # + Code for request invitations flow
    # +++++++++++++++++++++++++++++++++++++

    def action_invitation_request(self):
        if self.sender_id != self.env.user.partner_id:
            raise ValidationError(_('Only sender of the invitation can request the invitation'))
        template = self.env.ref('wallbox_ecommerce_extended.email_template_request_invitation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        self.status = 'pending'
        if not self.name:
            self.name = self.env['ir.sequence'].next_by_code('charging.station.invitation')

    def action_accept_request(self):
        if self.receiver_id != self.env.user.partner_id:
            raise ValidationError(_('Only owner of the charging station can accept the invitation request'))
        template = self.env.ref('wallbox_ecommerce_extended.email_template_request_invitation_accept', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        self.charging_station_id.allowed_partner_ids = [(4, self.sender_id.id)]
        self.status = 'accepted'

    def action_reject_request(self):
        if self.receiver_id != self.env.user.partner_id:
            raise ValidationError(_('Only owner of the charging station can Reject the invitation request'))
        template = self.env.ref('wallbox_ecommerce_extended.email_template_request_invitation_reject', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        self.status = 'rejected'

    # ++++++++++++++++++++++++++++++++
    # + Code for send invitations flow
    # ++++++++++++++++++++++++++++++++

    def action_send_invitation(self):
        if self.sender_id != self.env.user.partner_id:
            raise ValidationError(_('Only sender of the invitation can send the invitation request'))
            
        if self.receiver_id and not self.email:
            self.write({
                'user_name': self.receiver_id.name,
                'email': self.receiver_id.email,
                'mobile': self.receiver_id.mobile or self.receiver_id.phone
            })

        if not self.receiver_id and self.email:
            self.receiver_id = self.create_partner_user(name=self.user_name, email=self.email, mobile=self.mobile)

        template = self.env.ref('wallbox_ecommerce_extended.email_template_send_invitation', raise_if_not_found=False)
        if template:
            template.send_mail(self.id, force_send=True)
        self.status = 'pending'
        if not self.name:
            self.name = self.env['ir.sequence'].next_by_code('charging.station.invitation')

    def action_accept_invitation(self):
        if self.receiver_id != self.env.user.partner_id:
            raise ValidationError(_('Only Receiver can accept the invitation.'))
        template = self.env.ref('wallbox_ecommerce_extended.email_template_send_invitation_accept', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)
        self.charging_station_id.sudo().allowed_partner_ids = [(4, self.receiver_id.id)]
        self.status = 'accepted'

    def action_reject_invitation(self):
        if self.receiver_id != self.env.user.partner_id:
            raise ValidationError(_('Only Receiver can Reject the invitation request'))
        template = self.env.ref('wallbox_ecommerce_extended.email_template_send_invitation_reject', raise_if_not_found=False)
        if template:
            template.sudo().send_mail(self.id, force_send=True)
        self.status = 'rejected'

    # +++++++++++++++++++++++++++++++++++++
    # ++++++++++++++++END++++++++++++++++++
    # +++++++++++++++++++++++++++++++++++++
