# -*- coding: utf-8 -*-
{
    'name': "Reportes Facturas-Pagos",
    'summary': """Reportes (de cliente y a provedores) de facturas y sus respectivos pagos""",
    'author': "SIE Center / Samuel Santana",
    'category': 'Accounting',
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','sale','purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'reports/client_invoices_payments_report.xml',
        'reports/provider_invoices_payments_report.xml',
        #'views/menus.xml',
        'wizard/invoices_payments_report_wizard.xml',
    ],
}
