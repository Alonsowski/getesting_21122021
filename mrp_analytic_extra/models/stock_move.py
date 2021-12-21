# -*- coding: utf-8 -*-
from odoo import models

class StockMove(models.Model):
    _inherit = "stock.move"

    def _generate_valuation_lines_data(
        self,
        partner_id,
        qty,
        debit_value,
        credit_value,
        debit_account_id,
        credit_account_id,
        description,
    ):
        """
        Ensure Analytic Account is set on the journal items.
        Self is a singleton.
        """
        rslt = super()._generate_valuation_lines_data(
            partner_id,
            qty,
            debit_value,
            credit_value,
            debit_account_id,
            credit_account_id,
            description,
        )
        analytic_acc = (
            self.raw_material_production_id.analytic_account_id
            or self.production_id.analytic_account_id
        )
        analytic_tag = (
            self.raw_material_production_id.analytic_tag_id
            or self.production_id.analytic_tag_id
        )
        # only override analytic_account_id if not set
        if not self.analytic_account_id:
            self.analytic_account_id = analytic_acc
        if analytic_tag:
            self.tag_ids = [(4, analytic_tag.id)]
        for entry in rslt.values():
            if not entry.get("analytic_account_id") and analytic_acc:
                entry["analytic_account_id"] = analytic_acc.id
            if not entry.get("analytic_tag_ids") and analytic_tag:
                entry["analytic_tag_ids"] = [(4, analytic_tag.id)]
        return rslt
