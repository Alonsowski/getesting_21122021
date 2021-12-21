from odoo import api, models, _
from odoo.exceptions import ValidationError
import logging
_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def fix_analytic_accounts(self):
        manual_fix_ids = []
        for move in self:
            account = False
            force = False
            if move.journal_id.type == "sale":
                account = move.invoice_line_ids[0].analytic_account_id
            elif move.journal_id.type == "bank" and move.has_reconciled_entries:
                #buscar asientos consiliados o abrir wizard para seleccionar manualmente las cuentas
                rlines = self.env["account.move.line"].browse(move.line_ids._reconciled_lines())
                for line in rlines:
                    _logger.warning(f"reconcile line: {line.name}")
                    if line.analytic_account_id:
                        account = line.analytic_account_id
                        break
                force = True
            elif move.asset_id:
                account = move.asset_id.account_analytic_id
                
            if account:
                move.assign_analytic_account_if_empty(account, force)
            elif move.journal_id.type == "bank":
                _logger.warning(f"Not account found, adding lines to manual fix")
                manual_fix_ids.extend(move.line_ids.ids)
                _logger.warning(f"lines: {manual_fix_ids}")
        
        _logger.warning(f"Lines: {manual_fix_ids}")
        if manual_fix_ids:
            _logger.warning("Opening view...")
            return {
                "name": "Ajuste Manual de Cuentas Analíticas",
                "type": "ir.actions.act_window",
                "res_model": "account.move.line",
                "view_mode": "tree",
                "view_id": False,
                "views": [(self.env.ref("fix_analytic_acc.account_move_line_edit_analytic_accounts_view").id, "tree")],
                "domain": [("id", "in", manual_fix_ids)],
                "target": "new",
            }
    
    
    def assign_analytic_account_if_empty(self, account, force=None):
        self.ensure_one()
        for line in self.line_ids:
            if not line.analytic_account_id or force:
                line.analytic_account_id = account
        