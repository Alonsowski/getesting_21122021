# -*- coding: utf-8 -*-
from odoo import models

class ExpenseSheet(models.Model):
    _inherit ='hr.expense.sheet'

    def button_return_payment_to_post(self):
        self.ensure_one()
        self.state = "post"