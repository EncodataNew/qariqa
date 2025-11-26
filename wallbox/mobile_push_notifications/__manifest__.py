# -*- coding: utf-8 -*
# Part of 4Minds. See LICENSE file for full copyright and licensing details.

{
    'name': 'Mobile Push Notifications',
    'version': '18.0',
    'category': 'Tools',
    'summary': 'Manage Expo push tokens and send notifications',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/push_notification_views.xml',
    ],
    'installable': True,
    'application': False,
    "license": "LGPL-3",
}
