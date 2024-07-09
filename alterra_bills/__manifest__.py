# -*- coding: utf-8 -*-
{
    'name' : 'Alterra Bills',
    'version' : '14.0.1.0',
    'summary': 'Alterra Bills',
    'description': """
        Alterra Bills
    """,
    'category': 'Human Resources',
    'website': 'https://alterrabills.id',
    'depends' : [
        'base',
        'mail',
        'hr',
        ],
    'assets': {
        
    },
    'data' : [
        "employee/data/ir_cron.xml",
        "employee/data/ir_seq.xml",
        "employee/security/ir.model.access.csv",
        "employee/views/app_root.xml",
        "employee/views/queue_import_data_views.xml",
        "employee/wizard/hr_import_employee_wizard.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'license': 'LGPL-3',
}
