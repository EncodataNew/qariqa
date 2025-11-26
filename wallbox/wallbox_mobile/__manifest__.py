# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Mobile",
    "version": "18.0",
    "summary": "Wallbox Mobile",
    "description": """
       Wallbox mobile app connector.
    """,
    "category": 'Customization',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['wallbox_integration', 'mobile_push_notifications'],

    "data": [
        "security/ir.model.access.csv",
        "data/ir_config_parameter.xml",
        "data/mail_templates.xml",
        "views/wallbox_device_token_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
