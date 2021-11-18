# -*- coding: utf-8 -*-
# Part of AktivSoftware See LICENSE file for full copyright
# and licensing details.
{
    'name': "User Activity Log",

    'summary': """
        The module will show the recent activity of users""",

    'description': """
        The module will show the recent activity of users""",

    'author': "Aktiv Software",
    'website': "http://www.aktivsoftware.com",
    'category': 'Extra Tools',
    'version': '14.0.1.0.1',
    'license': "AGPL-3",
    'price': 7.00,
    'currency': "EUR",
    # any module necessary for this one to work correctly
    'depends': ['base', 'web'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/user_log_security.xml',
        'views/user_activity_view.xml',
        'views/custom_xml.xml',

    ],
    'qweb': ['static/src/xml/user_menu_template.xml'],
    'images': [
        'static/description/banner.jpg',
    ],
    'installable': True,
    'application': True
}
