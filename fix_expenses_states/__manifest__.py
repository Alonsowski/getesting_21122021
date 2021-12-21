# -*- coding: utf-8 -*-
{
    'name': "Regreso de estado Pagado a Aprobado",
    'summary': """Arreglo rápido a mal funcionamiento deribado de cancelar un pago: Se genera un botón el cual regresa el estado de la nota de gasto de pagado a aprobado, en caso de que el importe adeudado sea mayor a cero""",
    'author': "SIE Center / Samuel Santana",
    'category': 'Expenses',
    'version': '14.0.1.0.1',

    # any module necessary for this one to work correctly
    'depends': ['account','hr_expense'],

    # always loaded
    'data': [
        'views/hr_expense_sheet.xml',
    ],
}
