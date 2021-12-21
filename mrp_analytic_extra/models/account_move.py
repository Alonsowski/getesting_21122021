# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        pass