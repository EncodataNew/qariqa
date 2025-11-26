# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.
{
    "name": "Wallbox Ecommerce Extended",
    "version": "18.0",
    "summary": "Wallbox Ecommerce Extended",
    "description": """
        Forces subscription purchase with first wallbox purchase
        and handles subsequent subscription-only purchases.

        ** Configuration of product
        Subscription Product Configuration:
            is_wallbox_subscription = True for subscription.
            Product Type = service.

        IOT product Configuration:
            is_wallbox boolean = True for IOT Device.
            Product Type = combo.
            combo choice = Subscription Combo of that product.
    """,
    "category": 'Ecommerce',

    # Author
    "author": "4minds Technology",
    "website": "https://www.4mindstech.com",
    "license": "LGPL-3",

    # Dependency
    "depends": ['sale_management', 'website_sale', 'purchase', 'stock', 'wallbox_integration', 'wallbox_cms_server_integration'],

    "data": [
        "security/ir.model.access.csv",
        "security/security.xml",
        "security/charging_station_invitation_security.xml",
        "data/data.xml",
        "data/ir_cron.xml",
        "data/ir_sequence.xml",
        "data/mail_templates.xml",
        "views/product_template.xml",
        "views/templates.xml",
        "views/sale_order_views.xml",
        "views/wallbox_subscription_views.xml",
        "views/wallbox_order_views.xml",
        "views/request_charging_views.xml",
        "views/charging_station_views.xml",
        "views/wallbox_charging_session_views.xml",
        "views/wallbox_invoice_view.xml",
        "views/trip_views.xml",
        "views/user_vehicle_views.xml",
        "views/charging_station_invitation_views.xml",
    ],

    "installable": True,
    "application": False,
    "auto_install": False
}
