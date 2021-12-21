# -*-coding: utf-8 -*-
from odoo import fields, models


class MrpProduction(models.Model):
    _inherit = "mrp.production"

    analytic_tag_id = fields.Many2one(
        comodel_name="account.analytic.tag", string="Etiqueta Analítica"
    )
