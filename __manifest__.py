{
    'name': "Seminar",
    'version': "14.0.1.0",
    'sequence': "0",
    'depends': ['base', 'mail', 'web', 'logic_payments', 'leads'],
    'data': [
        'security/groups.xml',
        'security/export_visible_security.xml',
        'security/ir.model.access.csv',
        'security/rules.xml',
        'views/college_list.xml',
        'views/leads.xml',
        'views/expenses.xml',
        'views/incentive.xml',
        'views/export_hide.xml',
        'data/default_data.xml',
        'views/payments.xml',
        'views/km_traveling_rate.xml',
        'data/activity.xml',

    ],
    'demo': [],
    'summary': "logic_seminar_module",
    'description': "this_is_my_app",
    'installable': True,
    'auto_install': False,
    'license': "LGPL-3",
    'application': True
}
