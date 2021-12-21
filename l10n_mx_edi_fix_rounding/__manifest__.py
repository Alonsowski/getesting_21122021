# -*- coding: utf-8 -*-
{
    'name': "Arreglo al redondeo de tipo de cambio CFDI",

    'description': """
        Implementación de un checkbox que al marcarlo suma 1 a la cifra menos significativa de TipoCambioDR al momento de generar el CFDI.
    """,

    'author': "SIE Center / Samuel Santana",
    'website': "http://www.siecenter.com.mx",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
   
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'l10n_mx_edi'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_payment_view.xml',

    ],
}
