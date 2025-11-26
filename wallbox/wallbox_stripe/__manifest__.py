# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Stripe",
    "version": "18.0",
    "summary": "Wallbox Stripe connector",
    "description": """
       Wallbox stripe connector.
       This module add functionality for capture manual partial payment.
    """,
    "category": 'Customization',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['payment_stripe', 'wallbox_ecommerce_extended'],

    "data": [
        "views/sale_order_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": True,
}
