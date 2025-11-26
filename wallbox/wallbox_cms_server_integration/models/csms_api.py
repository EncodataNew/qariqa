# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

import json
import requests
import logging
from odoo.http import request
from odoo import models, fields, api, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

class CSMSAPI(models.AbstractModel):
    _name = 'csms.api'
    _description = 'CSMS API Client'

    # ========================================
    # Generic Auth & Make Request Controllers
    # ========================================
    def _get_api_credentials(self):
        """Get API URL and token from system parameters"""
        params = self.env['ir.config_parameter'].sudo()
        return {
            'url': params.get_param('cms.api.url'),
            'token': params.get_param('cms.api.token')
        }

    def _make_request(self, endpoint, method='GET', payload=None):
        """Generic method to make API requests"""
        credentials = self._get_api_credentials()

        if not credentials['url'] or not credentials['token']:
            raise UserError(_("CMS API credentials not configured in settings"))

        url = f"{credentials['url'].rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            'Authorization': f"Bearer {credentials['token']}",
            'Content-Type': 'application/json'
        }

        try:
            _logger.info(f"CSMS API Request: {method} {url}")
            if payload:
                _logger.debug("Request payload: %s", payload)

            # Convert payload to JSON string if it's a dict
            data = json.dumps(payload) if isinstance(payload, dict) else payload

            response = requests.request(
                method,
                url,
                headers=headers,
                data=data,
                timeout=10
            )

            # Log response details for debugging
            _logger.debug("Response status: %s", response.status_code)
            _logger.debug("Response content: %s", response.text)

            # Handle 204 No Content responses
            if response.status_code == 204:
                return True

            if response.status_code == 404:
                return None

            # For 400 errors, try to extract more detailed error message
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('detail', error_data)
                    raise UserError(_("CSMS API Validation Error: %s") % str(error_msg))
                except ValueError:
                    pass

            response.raise_for_status()
            
            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            _logger.error(f"CSMS API Error: {str(e)}")
            raise UserError(_("CSMS API Error: %s") % str(e))

    # ==============================
    # Charging Station Methods
    # ==============================
    def list_chargers(self):
        """List all chargers from CSMS"""
        return self._make_request('/api/v1/csms/chargers/', 'GET')

    def create_charger(self, charger_data):
        """
        Create a new charger in CSMS
        Required fields: charger_id, price_per_kwh
        """
        try:
            required_fields = ['charger_id', 'price_per_kwh']
            if not all(field in charger_data for field in required_fields):
                raise UserError(_("Missing required fields for charger creation"))

            # Convert numeric fields to strings and format data
            charger_data = self._prepare_charger_data(charger_data)

            _logger.debug("Attempting to create charger with data: %s", charger_data)
            response = self._make_request('/api/v1/csms/chargers/', 'POST', charger_data)

            if response is None:
                raise UserError(_("No response received from CSMS API"))

            if response.get('ws_url'):
                charging_station = request.env['charging.station'].browse(int(response.get('odoo_id')))
                if charging_station:
                    charging_station.ws_url = response.get('ws_url')

            _logger.info("Successfully created charger: %s", charger_data.get('charger_id'))
            return response

        except Exception as e:
            _logger.error("Failed to create charger. Data: %s. Error: %s", charger_data, str(e))
            raise UserError(_("Failed to create charger: %s") % str(e))

    def get_charger(self, charger_id):
        """Get charger details from CSMS by charger ID"""
        return self._make_request(f'/api/v1/csms/chargers/{charger_id}/', 'GET')

    def update_charger(self, charger_id, charger_data):
        """
        Full update of charger in CSMS
        Required fields: all mandatory fields per API spec
        """
        charger_data = self._prepare_charger_data(charger_data)
        return self._make_request(f'/api/v1/csms/chargers/{charger_id}/', 'PUT', charger_data)

    def partial_update_charger(self, charger_id, charger_data):
        """
        Partial update of charger in CSMS
        Only include fields that need updating
        """
        charger_data = self._prepare_charger_data(charger_data)
        return self._make_request(f'/api/v1/csms/chargers/{charger_id}/', 'PATCH', charger_data)

    def delete_charger(self, charger_id):
        """Delete charger from CSMS"""
        return self._make_request(f'/api/v1/csms/chargers/{charger_id}/', 'DELETE')

    def _prepare_charger_data(self, charger_data):
        """Convert numeric fields to strings and ensure proper formatting"""
        # Ensure all required fields are present
        required_fields = ['charger_id', 'price_per_kwh']
        for field in required_fields:
            if field not in charger_data:
                raise UserError(_("Missing required field: %s") % field)

        # Convert numeric fields to strings
        numeric_fields = ['price_per_kwh', 'latitude', 'longitude']
        for field in numeric_fields:
            if field in charger_data and charger_data[field] is not None:
                charger_data[field] = str(charger_data[field])

        # Format dates to ISO 8601 format
        if 'subscription_exp_date' in charger_data and charger_data['subscription_exp_date']:
            if isinstance(charger_data['subscription_exp_date'], str):
                # Parse existing string date
                try:
                    from datetime import datetime
                    dt = datetime.strptime(charger_data['subscription_exp_date'], '%d-%m-%Y')
                    charger_data['subscription_exp_date'] = dt.isoformat()
                except ValueError:
                    raise UserError(_("Invalid date format for subscription_exp_date. Use DD-MM-YYYY"))
            elif hasattr(charger_data['subscription_exp_date'], 'strftime'):
                # Handle date/datetime objects
                charger_data['subscription_exp_date'] = charger_data['subscription_exp_date'].isoformat()

        return charger_data

    def _prepare_rfid_data(self, odoo_charger):
        """Prepare RFID tag data for API sync"""
        return [{
            'tag_id': tag.tag_id,
            'is_allowed': tag.is_allowed,
        } for tag in odoo_charger.rfid_tag_ids]

    def sync_charger_status(self, odoo_charger):
        """
        Comprehensive sync between Odoo and CSMS
        Handles both creation and updates as needed
        """
        charger_data = {
            'odoo_id': odoo_charger.id,
            'owner_id': odoo_charger.owner_id.id if odoo_charger.owner_id else None,
            'charger_id': odoo_charger.charger_id,  # Using charger_id instead of charger_id
            'price_per_kwh': odoo_charger.price_per_kwh,
        }

        charger_data['rfid_tags'] = self._prepare_rfid_data(odoo_charger)

        if odoo_charger.wallbox_order_id and odoo_charger.wallbox_order_id.subscription_exp_date:
            charger_data['subscription_exp_date'] = odoo_charger.wallbox_order_id.subscription_exp_date.strftime('%d-%m-%Y')
        else:
            charger_data['subscription_exp_date'] = False

        # Add location if available
        if hasattr(odoo_charger, 'latitude') and hasattr(odoo_charger, 'longitude'):
            charger_data.update({
                'latitude': odoo_charger.latitude,
                'longitude': odoo_charger.longitude,
            })

        try:
            # First try to get existing charger
            existing = self.get_charger(odoo_charger.charger_id)
            if existing:
                odoo_charger.status = existing.get('status')
                # Update existing charger
                return self.partial_update_charger(odoo_charger.charger_id, charger_data)
            else:
                # Create new charger
                return self.create_charger(charger_data)

        except UserError as e:
            _logger.error(f"Failed to sync charger {odoo_charger.charger_id}: {str(e)}")
            raise

    # ======================
    # CSMS Server Commands
    # ======================
    def remote_start_transaction(self, charger_id, customer_id, max_limit, odoo_request_id, charging_power_limit=None):
        """
        Send remote start command to CSMS
        Args:
            charger_id (str): The charger ID to start
            customer_id (int): The customer ID initiating the charge
            max_limit (float): Maximum energy limit in kWh
            charging_power_limit (float, optional): Maximum power in kW
        Returns:
            dict: Response from CSMS
        Raises:
            UserError: If request fails
        """
        payload = {
            'charger_id': str(charger_id),
            'customer_id': int(customer_id),
            'max_limit': str(max_limit),
            'odoo_request_id': odoo_request_id,
        }

        if charging_power_limit is not None:
            payload['charging_power_limit'] = str(charging_power_limit)

        try:
            response = self._make_request(
                '/api/v1/csms/remote-start-transaction/',
                method='POST',
                payload=payload
            )
            
            # Check if response is a dictionary (success case from your CSMS API)
            if isinstance(response, dict) and response.get('status'):
                _logger.info(f"Remote start transaction successful for charger {charger_id}")
                return {'success': True, 'message': response['status']}
            
            _logger.info(f"Remote start transaction successful for charger {charger_id}")
            return response

        except UserError as e:
            _logger.error(f"Failed to start transaction for charger {charger_id}: {str(e)}")
            raise UserError(_("Failed to start charging session: %s") % str(e))

    def remote_stop_transaction(self, charger_id, transaction_id):
        """
        Send remote stop command to CSMS
        Args:
            charger_id (str): The charger ID to stop
            transaction_id (int/str): The transaction ID to stop
        Returns:
            dict: Response from CSMS
        Raises:
            UserError: If request fails
        """
        payload = {
            'charger_id': str(charger_id),
            'transaction_id': str(transaction_id)
        }

        try:
            response = self._make_request(
                '/api/v1/csms/remote-stop-transaction/',
                method='POST',
                payload=payload
            )

            _logger.info(f"Remote stop transaction successful for charger {charger_id}, transaction {transaction_id}")
            return response

        except UserError as e:
            _logger.error(f"Failed to stop transaction {transaction_id} for charger {charger_id}: {str(e)}")
            raise UserError(_("Failed to stop charging session: %s") % str(e))

    def unlock_connector(self, charger_id):
        """
        Send unlock connector command to CSMS
        Args:
            charger_id (str): The charger ID to unlock
        Returns:
            dict: Response from CSMS
        Raises:
            UserError: If request fails
        """
        payload = {
            'charger_id': str(charger_id)
        }

        try:
            response = self._make_request(
                '/api/v1/csms/unlock-connector/',
                method='POST',
                payload=payload
            )

            _logger.info(f"Unlock connector command successful for charger {charger_id}")
            return response

        except UserError as e:
            _logger.error(f"Failed to unlock connector for charger {charger_id}: {str(e)}")
            raise UserError(_("Failed to unlock connector: %s") % str(e))

    def reset_charger(self, charger_id, reset_type="Soft"):
        """
        Send reset command to charger via CSMS
        Args:
            charger_id (str): The charger ID to reset
            reset_type (str): Type of reset ("Soft" or "Hard")
        Returns:
            dict: Response from CSMS
        Raises:
            UserError: If request fails
        """
        # Validate reset type
        if reset_type not in ("Soft", "Hard"):
            raise UserError(_("Invalid reset type. Must be 'Soft' or 'Hard'"))

        payload = {
            'charger_id': str(charger_id),
            'reset_type': reset_type
        }

        try:
            response = self._make_request(
                '/api/v1/csms/reset/',
                method='POST',
                payload=payload
            )

            _logger.info(
                "Reset (%s) command successful for charger %s", 
                reset_type, charger_id
            )
            return response

        except UserError as e:
            _logger.error(
                "Failed to reset (%s) charger %s: %s",
                reset_type, charger_id, str(e)
            )
            raise UserError(_("Failed to reset charger: %s") % str(e))
