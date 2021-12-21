# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
#from odoo.fields import Datetime
from datetime import datetime
import pytz
import json
import logging
_logger = logging.getLogger(__name__)


class InvoicePaymentWizard(models.TransientModel):
    _name ='invoice.payment.wizard'
    
    start_date = fields.Date('Fecha de Inicio', required=True)
    end_date = fields.Date('Fecha de Fin', required=True)
    partner_type = fields.Selection([("customer", "Cliente"), ("supplier", "Proveedor")], string="Tipo de Contacto", required=True)
    customer_ids = fields.Many2many(comodel_name="res.partner", relation="invoice_payment_rel_customer", string="Clientes")
    supplier_ids = fields.Many2many(comodel_name="res.partner", relation="invoice_payment_rel_supplier", string="Proveedores")
    sale_journals = fields.Many2many(comodel_name="account.journal", relation="invoice_payment_rel_sale", string="Diario", domain=[('type', '=', 'sale')])
    purchase_journals = fields.Many2many(comodel_name="account.journal", relation="invoice_payment_rel_purchase", string="Diario", domain=[('type', '=', 'purchase')])
    analytic_account_ids = fields.Many2many(comodel_name="account.analytic.account", string="Cuenta Analítica")
    company_id = fields.Many2one('res.company', required=True, default = lambda self:self.env.user.company_id)
    pending_payment_filter = fields.Boolean(string="Facturas con pagos pendientes")
    paid_invoices_filter = fields.Boolean(string="Facturas completamente pagadas")
    sel_payment_status = [
        ('not_paid', 'Pago pendiente'),
        ('in_payment', 'En proceso'),
        ('paid', 'Pagado'),
        ('partial', 'Pagado parcialmente'),
        ('reversed', 'Revertido'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
    ]
    payment_status = fields.Selection(sel_payment_status, string="Estado de pago")
    show_not_all_partners = fields.Boolean(string="Mostrar solo contactos con facturas")
    
    def get_data(self):
        result = []
        partners = []
        journals = []
        if self.partner_type == "customer":
            partners = self.customer_ids
            journals = self.sale_journals.ids
        else:
            partners = self.supplier_ids
            journals = self.purchase_journals.ids
        if not partners:
            partners = self.env["res.partner"].search([("customer_rank", ">", 0)]) if self.partner_type == "customer" else self.env["res.partner"].search([("supplier_rank", ">", 0)])
        for partner in partners:
            partner_info = {
                "partner_name": partner.name,
                "partner_address": (partner.street_name or "") + " " + (partner.street_number or "") + " " + (partner.street_number2 or ""),
                "partner_city": partner.city or "",
                "partner_state": partner.state_id.name or "",
                "partner_country": partner.country_id.name or "",
                "partner_rfc": partner.vat or "",
                "currency_id": partner.currency_id.id, 
            }
            invoice_domain = [
                ("partner_id", "child_of", partner.id),
                ("state", "=", "posted"),
            ]
            invoice_domain.append(("date", ">=", self.start_date))
            invoice_domain.append(("date", "<=", self.end_date))
            if self.partner_type == "customer":
                invoice_domain.append(("move_type", "=", "out_invoice"))
            else:
                invoice_domain.append(("move_type", "=", "in_invoice"))
            #_logger.warning("-.-.-.-. Pasa dominios de facturas .-.-.-.-")
            invoices = self.env["account.move"].search(invoice_domain)
            #_logger.warning("-.-.-.-. Pasa búsqueda de facturas .-.-.-.-")
            if self.analytic_account_ids:
                invoices = invoices.filtered(lambda inv: inv.invoice_line_ids[0].analytic_account_id.id in self.analytic_account_ids.ids)
            if self.pending_payment_filter:
                invoices = invoices.filtered(lambda inv: inv.payment_state in ['not_paid', 'partial'])
            if self.paid_invoices_filter:
                invoices = invoices.filtered(lambda inv: inv.payment_state in ['paid', 'in_payment'])
            if self.payment_status:
                invoices = invoices.filtered(lambda inv: inv.payment_state == self.payment_status)
            if journals:
                invoices = invoices.filtered(lambda inv: inv.journal_id.id in journals)            
            #_logger.warning("-.-.-.-. Pasa filtros de facturas .-.-.-.-")
            partner_invoices = []
            saldo = 0.00
            currencies = {}
            for invoice in invoices:
                state_dict = {
                    'not_paid': 'Pago pendiente',
                    'in_payment': 'En proceso',
                    'paid': 'Pagado',
                    'partial': 'Pagado parcialmente',
                    'reversed': 'Revertido',
                    'invoicing_legacy': 'Invoicing App Legacy',
                    False: ''
                }
                invoice_info = {
                    "invoice_name": invoice.name,
                    "invoice_pay_ref": invoice.payment_reference or "",
                    "invoice_ref": invoice.ref or "",
                    "invoice_date": invoice.invoice_date,
                    "invoice_due": invoice.invoice_date_due,
                    "invoice_analytic": invoice.invoice_line_ids[0].analytic_account_id.code,
                    "invoice_journal": invoice.journal_id.name,
                    "invoice_policy": invoice.l10n_mx_edi_payment_policy,
                    "invoice_state": state_dict[invoice.payment_state],
                    "invoice_currency": invoice.currency_id.name,
                    "invoice_amount": invoice.amount_total,
                }
                #_logger.warning("-.-.-.-. Pasa invoice_info .-.-.-.-")

                reverse_cons = -1
                if not invoice.currency_id.name in currencies.keys():
                    currencies[invoice.currency_id.name] = 0.0
                saldo = invoice_info["invoice_amount"]
                invoice_payments_widget = json.loads(invoice.invoice_payments_widget)
                payments = invoice_payments_widget["content"] if invoice_payments_widget else {}
                filtered_payments = []
                _logger.warning(invoice_payments_widget)
                for item in payments:
                    # if datetime.strptime(item['date'], '%Y-%m-%d').date() > self.end_date:
                    #     continue
                    _logger.warning(f"-.-.-.-. Factura: {invoice.name} ID: {invoice.id} .-.-.-.-")
                    item["account_payment_id"] = self.env["account.payment"].browse(item["account_payment_id"]) if item["account_payment_id"] else ""
                    #item["payment_id"] = self.env["account.payment"].browse(item["payment_id"]) if item["payment_id"] else ""
                    item["analytic"] = item["account_payment_id"].analytic_account_id.code if item["account_payment_id"] and item["account_payment_id"].analytic_account_id else ""
                    if not item["analytic"]:
                        item["analytic"] = invoice_info["invoice_analytic"]
                    item['amount'] = item['amount'] * reverse_cons
                    saldo += item['amount']
                    filtered_payments.append(item)
                invoice_info["payments"] = filtered_payments
                invoice_info["total"] = saldo
                partner_invoices.append(invoice_info)
            partner_info["invoices"] = partner_invoices
            for currency in currencies:
                positive_total = 0.0
                for inv in partner_invoices:
                    if inv['invoice_currency'] == currency:
                        positive_total += inv['invoice_amount']
                        for p in inv["payments"]:
                            positive_total += p['amount']
                currencies[currency] = positive_total
            partner_info["currencies"] = currencies
            result.append(partner_info)
        return result
        
    
    def print_pdf(self):
        aa = ",".join(self.analytic_account_ids.mapped("code")) if self.analytic_account_ids else ""
        if self.partner_type == "customer":
            journals = ",".join(self.sale_journals.mapped("name")) if self.sale_journals else ""
        else:
            journals = ",".join(self.purchase_journals.mapped("name")) if self.purchase_journals else ""
        payment_filters = ""
        if self.pending_payment_filter:
            payment_filters = "Pago pendiente, Pagado parcialmente"
        if self.paid_invoices_filter:
            payment_filters = "Pagado, En Proceso"
        if self.payment_status:
            state_dict = {
                    'not_paid': 'Pago pendiente',
                    'in_payment': 'En proceso',
                    'paid': 'Pagado',
                    'partial': 'Pagado parcialmente',
                    'reversed': 'Revertido',
                    'invoicing_legacy': 'Invoicing App Legacy',
                }
            payment_filters = state_dict[self.payment_status]
        data = {
            "partners": self.get_data(),
            "analytic_accounts": aa,
            "journals": journals,
            "payment_filters": payment_filters,
            "start": self.start_date,
            "end": self.end_date,
            "not_show_all": self.show_not_all_partners,
        }
        if self.partner_type == "customer":
            return self.env.ref('sie_facturas_pagos.client_invoices_payments_report').report_action(self, data)
        else:
            return self.env.ref('sie_facturas_pagos.provider_invoices_payments_report').report_action(self, data)
    
    # def get_date(self):
    #     start_date = datetime.strptime(str(self.start_date), '%Y-%m-%d').date()
    #     #start_date = self.start_date.strftime('%d-%m-%Y')
    #     end_date = datetime.strptime(str(self.end_date), '%Y-%m-%d').date()
    #     #end_date = self.end_date.strftime('%m-%d-%Y')        
        
    #     data = {'start_date':start_date , 'end_date':end_date}
    #     return data
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
