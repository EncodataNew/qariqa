# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    date_of_birth = fields.Date(string="Date of Birth")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')],
    string="Gender")

    # ++++++++++++++++++++
    # Wallbox owner fields
    # ++++++++++++++++++++
    type_of_ownership = fields.Selection([
        ('individual', 'Individual'),
        ('company', 'Company'),
        ('assigner', 'Assigner')
    ], string="Type of Ownership")
    ownership_percentage = fields.Float(string="Ownership Percentage")
    rental_status = fields.Selection([
        ('owner_occupied', 'Owner-Occupied'),
        ('rented_out', 'Rented Out')
    ], string="Rental Status")
    lease_agreement_details = fields.Text(string="Lease Agreement Details")
    property_tax_information = fields.Text(string="Property Tax Information")
    maintenance_fees = fields.Float(string="Maintenance Fees")
    legal_disputes = fields.Text(string="Legal Disputes")
    compliance_documents = fields.Binary(string="Compliance Documents")

    # +++++++++++++++++++++++++
    # Wallbox manager fields
    # +++++++++++++++++++++++++
    start_date = fields.Date(string='Start Date in Role')
    end_date = fields.Date(string='End Date in Role')
    responsibilities = fields.Text(string='Responsibilities')
    maintenance_coordination = fields.Boolean(string='Maintenance Coordination')
    budget_management = fields.Boolean(string='Budget and Expense Management')
    compliance_safety = fields.Boolean(string='Compliance and Safety Checks')
    tenant_relations = fields.Boolean(string='Tenant/Resident Relations')
    supplier_contracts = fields.Boolean(string='Contracts and Supplier Management')
    incident_reporting = fields.Binary(string='Incident and Issue Reporting')
    legal_compliance = fields.Binary(string='Legal and Regulatory Compliance')

    # +++++++++++++++++++++++++++++
    # Wallbox Technical Flag Fields
    # +++++++++++++++++++++++++++++
    is_technician = fields.Boolean(string='Is Technician')
    is_guest = fields.Boolean(string='Is Guest')
    is_wallbox_user = fields.Boolean(string='Is Wallbox User')
    is_condominium_owner = fields.Boolean(string='Is Condominium owner')

    # +++++++++++++++++++++++++++++
    # Customer Property Fields
    # +++++++++++++++++++++++++++++
    condominium_id = fields.Many2one('condominium.condominium', string='Condominium')
    building_id = fields.Many2one('building.building', string='Building',domain="[('condominium_id', '=?', condominium_id)]")
    parking_space_id = fields.Many2one('parking.space', string='Parking Space',domain="[('building_id', '=?', building_id)]")

    # +++++++++++++++++++++++++++++
    # All O2M Fields
    # +++++++++++++++++++++++++++++
    managed_building_ids = fields.One2many('building.building', 'manager_id', string='Managed Buildings')
    managed_condominium_ids = fields.One2many('condominium.condominium', 'manager_id', string='Managed Condominium')
    vehicle_ids = fields.One2many('user.vehicle', 'partner_id', string='Vehicle')

    building_ids = fields.One2many('building.building', 'owner_id', string='Owned Buildings')
    condominium_ids = fields.One2many('condominium.condominium', 'owner_id', string='Owned Condominium')
    parking_space_ids = fields.One2many('parking.space', 'owner_id', string='Owned Parking Space')

    charging_station_ids = fields.Many2many(
        'charging.station',
        'charging_station_partner_rel',
        'partner_id',
        'charging_station_id',
        string='Charging Stations',
        help='Charging stations associated with this partner'
    )

    def invite_wallbox_user(self):
        portal_wizard = self.env['portal.wizard'].sudo().with_context(active_ids=[self.id]).create({})
        portal_user = portal_wizard.user_ids
        portal_user.invite_wallbox_user()

    def action_show_users(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("base.action_res_users")
        action['domain'] = [('id', 'in', self.user_ids.ids)]
        form_view_id = self.env.ref('base.view_users_form').id
        action['views'] = [(False, 'list'), (form_view_id, 'form')]
        if len(self.user_ids) == 1:
            action['res_id'] = self.user_ids.id
            action['views'] = [(form_view_id, 'form')]
        return action


class PortalWizardUser(models.TransientModel):
    _inherit = 'portal.wizard.user'

    def invite_wallbox_user(self):
        self.ensure_one()
        self._assert_user_email_uniqueness()

        if self.is_portal or self.is_internal:
            raise UserError(_('The partner "%s" already has the portal access.', self.partner_id.name))

        # group_portal = self.env.ref('base.group_portal')
        # group_public = self.env.ref('base.group_public')
        group_user = self.env.ref("base.group_user")
        wallbox_user = self.env.ref("wallbox_integration.group_wallbox_user")
        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')

        self._update_partner_email()
        user_sudo = self.user_id.sudo()

        if not user_sudo:
            # create a user if necessary and make sure it is in the portal group
            company = self.partner_id.company_id or self.env.company
            user_sudo = self.sudo().with_company(company.id)._create_user()

        if not user_sudo.active or not self.is_portal:
            user_sudo.write({'active': True, 'groups_id': [(4, group_user.id), (4, wallbox_user.id), (3, group_public.id), (3, group_portal.id)]})
            # prepare for the signup process
            user_sudo.partner_id.signup_prepare()

        self.with_context(active_test=True)._send_email()

        return self.action_refresh_modal()

    def action_grant_access(self):
        """Grant the portal access to the partner.

        If the partner has no linked user, we will create a new one in the same company
        as the partner (or in the current company if not set).

        An invitation email will be sent to the partner.
        """
        self.ensure_one()
        self._assert_user_email_uniqueness()

        if self.is_portal or self.is_internal:
            raise UserError(_('The partner "%s" already has the portal access.', self.partner_id.name))

        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')

        self._update_partner_email()
        user_sudo = self.user_id.sudo()

        if not user_sudo:
            # create a user if necessary and make sure it is in the portal group
            company = self.partner_id.company_id or self.env.company
            user_sudo = self.sudo().with_company(company.id)._create_user()

        if not user_sudo.active or not self.is_portal:
            context = self.env.context
            if context.get('is_technician') or context.get('is_wallbox_user') or context.get('is_condominium_owner'):
                user_sudo.write({'active': True, 'groups_id': [(3, group_portal.id), (3, group_public.id)]})
            else:
                user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
            # prepare for the signup process
            user_sudo.partner_id.signup_prepare()

        self.with_context(active_test=True)._send_email()

        return self.action_refresh_modal()
