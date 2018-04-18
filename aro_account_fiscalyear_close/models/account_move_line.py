# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    @api.multi
    def get_agency_account_balance(self):
        """
        compute balance of account by agency
        return dict with debit, credit and balance
        """
        res = {
            'debit': round(sum(self.mapped('debit')),2),
            'credit': round(sum(self.mapped('credit')),2)
        }
        balance = res.get('debit', 0) - res.get('credit')
        res['balance'] = round(balance,2)
        return res


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def recompute_debcred(self):
        logger.info('recompute')
        # model = self.env['account.account']
        self.env.add_todo(self._fields['debit'], self.search([('code', '=', '101301')]))
        self.recompute()
        self.env.cr.commit()

