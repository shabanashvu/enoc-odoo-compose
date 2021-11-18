# -*- coding: utf-8 -*-
{
    'name': "SW - HR Attendance Work Hours",
    'summary': "Enhancement on Odoo's Attendances.",
    'description': """
        The module adds the following:
            - Columns to Odoo's Attendance Report to calculate the following (Taking any applied leaves into consideration):
                - In Work Hours
                - Out Work Hours
                - Late Minutes
                - Early Checkout
            - A 'Grace Period' field per shift on the Working Time.
    """,
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'HR',
    'version': '1.2',
    'depends': ['base', 'hr_contract', 'hr_attendance', 'resource','hr_holidays'],
    'installable': True,
    'auto_install': False,
    'data': [
        'views/hr_attenadnce_views.xml',
        'security/ir.model.access.csv',
    ],
    'post_init_hook': 'post_init_hook',
}
