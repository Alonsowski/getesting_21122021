# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.depends('procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids')
    def _compute_mrp_production_count(self):
        for sale in self:
            sale.mrp_production_count = len(sale.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids)
            for prod in sale.procurement_group_id.stock_move_ids.created_production_id.procurement_group_id.mrp_production_ids:
                prod.analytic_tag_id = sale.order_line[0].analytic_tag_ids[0] if sale.order_line and sale.order_line[0].analytic_tag_ids else False
                prod.analytic_account_id = sale.analytic_account_id
