# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox CMS Server Integration",
    "version": "18.0",
    "summary": "Wallbox CMS Server Integration",
    "description": """
       This module contains the functionality for communicate with CMS server.
    """,
    "category": 'Customization',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['base'],

    "data": [
        # "security/ir.model.access.csv",
        "views/res_config_setting_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
