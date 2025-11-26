# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Integration",
    "version": "18.0",
    "summary": "Wallbox Integration",
    "description": """
       Wallbox Integration for ev charging cars.
    """,
    "category": 'Customization',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['base', 'mail', 'product'],

    "data": [
        "security/security.xml",
        "security/security_condo.xml",
        "security/ir.model.access.csv",
        "data/ir_sequence.xml",
        "data/scheduled_actions.xml",
        "views/condominium_condominium_view.xml",
        "views/building_building_view.xml",
        "views/res_users_view.xml",
        "views/res_partner_view.xml",
        "views/parking_space_view.xml",
        "views/charging_station_view.xml",
        "views/wallbox_order_view.xml",
        "views/wallbox_installation_view.xml",
        "views/service_view.xml",
        "views/product_template_views.xml",
        "views/wallbox_charging_session_view.xml",
        "views/user_vehicle_views.xml",
        "views/wallbox_log_views.xml",
        "views/error_log_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
