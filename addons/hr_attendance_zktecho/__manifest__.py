# -*- coding: utf-8 -*-
{
    'name': "SW - HR Attendance ZKTeco",
    'summary': """Integration with ZKTeco Biometric Devices""",
    'description': "",
    'license':  "Other proprietary",
    'author': "Smart Way Business Solutions",
    'website': "https://www.smartway.co",
    'category': 'Human Resources',
    'version': '1.4',
    'depends': ['base', 'hr', 'hr_contract', 'hr_attendance', 'resource','hr_attendance_work_hours'],
    'data': [
        'data/zk_techo_data.xml',
        'security/biometricdevice_security.xml',
        'security/ir.model.access.csv',
        'views/res_config_settings_view.xml',
        'views/hr_attendance_view.xml',
        'views/biometricdevice_view.xml',
        'views/hr_extensionview.xml',
        'wizard/move_attendance_wizard_view.xml',
        'wizard/generate_missing_attendance.xml',
    ],
    'images':  ["static/description/image.png"],
    'price' : 160,
    'currency' :  'EUR',
    'installable': True,
    'auto_install': False,
    'application':False,   
    'external_dependencies': {
        'python' : ['pyzk'],
    }, 
}
