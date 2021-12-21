# -*-coding: utf-8 -*-
{
    "name": "Analytic for manufacturing (extra)",
    "summary": "Adds the analytic tag to the production order",
    "version": "14.0.1.0.0",
    "category": "Manufacturing",
    'author': "SIE Center / Samuel Santana",
    'website': "http://www.siecenter.com.mx",
    "depends": ["mrp_analytic", "bi_picking_analytic", "stock"],
    "data": [
        'security/ir.model.access.csv',
        "views/mrp_view.xml",
        "views/stock_quant.xml",
    ],
}
