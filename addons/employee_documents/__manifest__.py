# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Employee Documents',
    'version': '14.0.0',
    'category': 'Human Resources',
    'summary': 'Employee Documents module for Enoc Links',
    'description': "",
    'website': 'https://biztras.com/',
    'depends': [ 'base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_documents_views.xml',
    ],
    'installable': True,
    'auto_install': True,
    'application':False,
    'license': 'OEEL-1',
}
