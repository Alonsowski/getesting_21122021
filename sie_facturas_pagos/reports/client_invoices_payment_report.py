# -*-coding: utf-8 -*-
from odoo import models

class ClientReport(models.AbstractModel):
    _name = 'report.sie_facturas_pagos.client_invoices_payments_template'

    def _get_report_values(self, docids, data=None):
        company = self.env.company
        currency = self.env['res.currency'].browse(data['partners'][0]['currency_id'])
        return {'doc_ids': docids, 'data': data, 'company': company, 'currency': currency}
