# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Attendance Report XLS',
    'version': '14.0.1.1',
    'category': 'Attendances',
    'summary': 'Custom Attendance XLS Report for Enoc Link',
    'description': "",
    'website': 'www.biztras.com',
    'depends': ['hr_attendance', 'report_xlsx', 'hr_custom', 'hr_attendance_zktecho'],
    'data': [
        'security/ir.model.access.csv',
        'report/report.xml',
        'views/hr_attendance_report_view.xml',
        'views/hr_attendance_filter.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'OEEL-1',
}