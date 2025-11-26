from odoo import http
from odoo.http import request
from datetime import datetime, timedelta

class DashboardController(http.Controller):

    @http.route('/wallbox_dashboard/data', type='json', auth='user')
    def get_dashboard_data(self):
        """Prepare all dashboard data with security checks"""
        user = request.env.user
        return {
            'summary': self._get_summary_stats(user),
            'recent_orders': self._get_recent_orders(user),
            'installation_status': self._get_installation_status(user),
            'charging_activity': self._get_charging_activity(user),
            'station_status': self._get_station_status(user),
            'alerts': self._get_alerts(user),
        }

    def _get_summary_stats(self, user):
        """Key performance indicators"""
        domain = self._get_base_domain(user)
        user = request.env.user
        partner = user.partner_id
        company = partner.country_id
        currency_symbol = company.currency_id.symbol if company.currency_id else ""
        return {
            'user_id': user.id,
            'partner_id': partner.id,
            'total_wallbox_orders': request.env['wallbox.order'].search_count(domain),
            'total_stations': request.env['charging.station'].search_count(domain),
            'active_sessions': request.env['wallbox.charging.session'].search_count([
                ('status', '=', 'Started')
            ] + domain),
            'pending_installations': request.env['wallbox.installation'].search_count([
                ('state', 'in', ['draft', 'confirmed', 'scheduled'])
            ] + domain),
            'revenue': sum(
                request.env['wallbox.charging.session'].search(domain).mapped('cost')
            ),
            'condominium_count': request.env['condominium.condominium'].search_count(domain),
            'building_count': request.env['building.building'].search_count(domain),
            'parking_space_count': request.env['parking.space'].search_count(domain),
            'user_count': request.env['res.partner'].search_count(domain),
            'total_my_charging_request': request.env['request.charging'].search_count([('request_user_id', '=', partner.id)]),
            'total_guest_charging_request': request.env['request.charging'].search_count([('request_user_id', '!=', partner.id)]),
            'total_wallbox_sale_order': request.env['sale.order'].search_count([('request_charging_id', '!=', False)]),
            'total_invoice': request.env['account.move'].search_count([('user_id', '=', user.id)]),
            'my_amount_total': sum(request.env['request.charging'].search([('request_user_id', '=', partner.id)]).mapped('amount_total')),
            'guest_amount_total': sum(request.env['request.charging'].search([('request_user_id', '!=', partner.id)]).mapped('amount_total')),
            'total_sale_order': sum(request.env['sale.order'].search([('request_charging_id', '!=', False)]).mapped('amount_total')),
            'total_invoice_amount': sum(request.env['account.move'].search([('user_id', '=', user.id)]).mapped('amount_untaxed_in_currency_signed')),
            'currency_symbol': currency_symbol,
        }

    def _get_recent_orders(self, user):
        """Last 5 wallbox orders"""
        domain = self._get_base_domain(user)
        return request.env['wallbox.order'].search_read(
            domain,
            ['name', 'customer_id', 'product_id', 'state', 'installation_date'],
            limit=5,
            order='create_date DESC'
        )

    def _get_installation_status(self, user):
        """Installation progress"""
        domain = self._get_base_domain(user)
        return request.env['wallbox.installation'].read_group(
            [('state', '!=', 'draft')] + domain,
            ['state'],
            ['state']
        )

    def _get_charging_activity(self, user):
        """Weekly charging activity"""
        domain = self._get_base_domain(user)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        # sessions = request.env['wallbox.charging.session'].search_read([
        #     ('start_time', '>=', start_date),
        #     ('start_time', '<=', end_date)
        # ] + domain, ['start_time', 'total_energy', 'cost'])

        sessions = request.env['wallbox.charging.session'].search_read([], 
            ['start_time', 'total_energy', 'cost'])

        return {
            'sessions': sessions,
            'total_energy': sum(session['total_energy'] for session in sessions),
            'total_cost': sum(session['cost'] for session in sessions),
        }

    def _get_station_status(self, user):
        """Charging station status breakdown"""
        domain = self._get_base_domain(user)
        return request.env['charging.station'].read_group(
            domain,
            ['status'],
            ['status']
        )

    def _get_alerts(self, user):
        """Critical alerts for the dashboard"""
        domain = self._get_base_domain(user)
        return {
            'faulted_stations': request.env['charging.station'].search_count([
                ('status', '=', 'Faulted')
            ] + domain),
            'overdue_maintenance': request.env['charging.station'].search_count([
                ('next_scheduled_maintenance', '<', datetime.now())
            ] + domain),
        } 

    def _get_base_domain(self, user):
        """Apply security rules based on user group"""
        if user.has_group('wallbox_integration.group_wallbox_admin'):
            return []
        elif user.has_group('wallbox_integration.group_wallbox_condo_owner'):
            return [('condominium_id.owner_id', '=', user.partner_id.id)]
        elif user.has_group('wallbox_integration.group_wallbox_user'):
            return [('customer_id', '=', user.partner_id.id)]
        elif user.has_group('wallbox_integration.group_wallbox_technician'):
            return [('installation_technician_id', '=', user.partner_id.id)]
        return [('id', '=', -1)]  # Default: no access
