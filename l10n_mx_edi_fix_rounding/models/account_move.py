# -*- coding: utf-8 -*-
from odoo import api, fields, models

import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_process_edi_web_services(self):
        docs = self.edi_document_ids.filtered(lambda d: d.state in ('to_send', 'to_cancel'))
        if 'blocking_level' in self.env['account.edi.document']._fields:
            docs = docs.filtered(lambda d: d.blocking_level != 'error')
        _logger.warning(f"docs: {docs}")
        docs._process_documents_web_services(with_commit=False)
