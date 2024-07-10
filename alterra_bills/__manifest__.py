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
        'queue_job',
        ],
    'assets': {
        
    },
    'data' : [
        "employee/data/ir_seq.xml",
        "employee/data/ir_mail_server.xml",
        "employee/data/import_mail_template.xml",
        "employee/security/ir.model.access.csv",
        "employee/wizard/hr_import_employee_wizard.xml",
        "employee/views/app_root.xml",
    ],
    'installable': True,
    'application': True,
    'sequence': 1,
    'license': 'LGPL-3',
}
