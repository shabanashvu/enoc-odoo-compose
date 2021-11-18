# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Custom',
    'version': '14.0.1',
    'category': 'Human Resources',
    'summary': 'Custom HR module for Enoc Links',
    'description': "",
    'website': 'https://biztras.com/',
    'depends': ['hr_gamification', 'base','hr','hr_holidays','hr_payroll','hr_attendance'],
    'data': [
        'data/hr_attendance_data.xml',
        'security/security_view.xml',
        'security/ir.model.access.csv',
        'views/hr_custom_views.xml',
        'wizard/attendance_date_views.xml'
    ],
    'installable': True,
    'auto_install': True,
    'application':True,
    'license': 'OEEL-1',
}
