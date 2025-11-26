from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # General Information
    is_wallbox_device = fields.Boolean(string="Is Wallbox Device?")
    # is_wallbox = fields.Boolean(string='Is Wallbox')
    # wallbox_id = fields.Char(string="ID")
    # wallbox_type = fields.Selection([
    #     ('residential', 'Residential'),
    #     ('public', 'Public'),
    #     ('commercial', 'Commercial'),
    # ], string="Type")

    # Technical Features
    charging_power = fields.Selection([
        ('3.7', '3.7 kW'),
        ('7.4', '7.4 kW'),
        ('11', '11 kW'),
        ('22', '22 kW'),
        ('other', 'Other'),
    ], string="Charging Power (kW)")

    voltage = fields.Selection([
        ('230v', '230V (single-phase)'),
        ('400v', '400V (three-phase)'),
    ], string="Voltage (V)")

    max_current = fields.Char(string="Max Current (A)")
    connector_type = fields.Selection([
        ('type1', 'Type 1'),
        ('type2', 'Type 2'),
        ('ccs', 'CCS'),
        ('chademo', 'CHAdeMO'),
    ], string="Connector Type")

    cable_length = fields.Char(string="Cable Length (m)")
    connectivity = fields.Selection([
        ('wifi', 'Wi-Fi'),
        ('bluetooth', 'Bluetooth'),
        ('ethernet', 'Ethernet'),
        ('4g', '4G'),
    ], string="Connectivity")

    communication_protocol = fields.Selection([
        ('ocpp1.6', 'OCPP 1.6'),
        ('ocpp2.0.1', 'OCPP 2.0.1'),
    ], string="Communication Protocol")

    user_authentication = fields.Selection([
        ('rfid', 'RFID'),
        ('pin', 'PIN'),
        ('app', 'App'),
    ], string="User Authentication")

    load_management = fields.Boolean(string="Load Management")
    solar_compatibility = fields.Boolean(string="Solar Compatibility")

    residual_current_protection = fields.Selection([
        ('type_a', 'Type A'),
        ('type_b', 'Type B'),
        ('integrated', 'Integrated'),
        ('external', 'External required'),
    ], string="Residual Current Protection")

    protection_rating = fields.Char(string="Protection Rating (IP/IK)")
    min_operating_temp = fields.Float(string="Min Operating Temperature (°C)")
    max_operating_temp = fields.Float(string="Max Operating Temperature (°C)")
    dimensions = fields.Char(string="Dimensions (mm)")
    weight = fields.Float(string="Weight (kg)")
    installation_method = fields.Selection([
        ('wall_mounted', 'Wall-mounted'),
        ('pedestal_mounted', 'Pedestal-mounted'),
    ], string="Installation Method")

    safety_standards = fields.Char(string="Safety Standards")
    certifications = fields.Char(string="Certifications")
    indicative_price = fields.Float(string="Indicative Price (€)")
