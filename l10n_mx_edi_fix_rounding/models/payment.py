# -*- coding: utf-8 -*-
from odoo import models, fields

class account_payment(models.Model):
    _inherit = "account.payment"

    force_rounding = fields.Boolean(string='Forzar Redondeo (Tipo de cambio)')