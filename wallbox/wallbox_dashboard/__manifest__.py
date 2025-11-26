# -*- coding: utf-8 -*
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Dashboard",
    "version": "18.0",
    "summary": "Wallbox Dashboard",
    "description": """
       TASK ID - 
    """,
    "category": 'Customization',

    # Author
    "author": "4Minds technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['wallbox_ecommerce_extended'],

    "data": [
        # "security/ir.model.access.csv",
        "views/dashboard_views.xml",
    ],

    'assets': {
        'web.assets_backend': [
            'wallbox_dashboard/static/src/scss/dashboard.scss',
            'wallbox_dashboard/static/src/js/dashboard_action.js',
            'wallbox_dashboard/static/src/xml/dashboard_template.xml',
        ],
    },

    "installable": True,
    "application": False,
    "auto_install": False
}
