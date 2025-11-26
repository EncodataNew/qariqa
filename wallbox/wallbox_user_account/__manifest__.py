# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox User Account",
    "version": "17.0",
    "summary": "Wallbox User Account",
    "description": """
       - This module add a functionality for Wallbox User Account (Third party vendors can be login to the system as a reseller).
       - reseller user can manage it's OWN related data.
       - Security and Access rights will be managed for each model, menus and records.
    """,
    "category": 'e-commerce',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['website_sale', 'wallbox_integration'],

    "data": [
        "data/data.xml",
        "views/auth_singup_login_template.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
