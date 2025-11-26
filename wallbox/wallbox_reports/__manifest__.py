# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Reports",
    "version": "18.0",
    "summary": "Wallbox Reports",
    "description": """
       Wallbox Reports
    """,
    "category": 'Reports',

    # Author
    "author": "Bahelim Munafkhan",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['wallbox_ecommerce_extended'],

    "data": [
        "security/ir.model.access.csv",
        "reports/wallbox_order/wallbox_order_report.xml",
        "reports/wallbox_order/wallbox_order_report_action.xml",
        "reports/wallbox_installation/wallbox_installation_reort.xml",
        "wizard/wall_box_charging_session_wizard_views.xml",
        "reports/charging_session/charging_session_report.xml",
        "views/charging_station_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
