# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


LIST_ACCOUNT = [
    '466550', '466500', '466050', '466000', '465000', '463900', '463100',
    '425200', '425100', '425000', '424850', '424800', '411200', '411100',
    '410000', '408000', '404000', '400800', '400000', '233605', '233600',
    '233500', '410500']


class AccountAccount(models.Model):
    _inherit = 'account.account'

    @api.model
    def set_account_reconcile(self):
        """
        Set reconcile to True for all account in LIST_ACCOUNT above
        """
        acc_set = self.search([('code', 'in', LIST_ACCOUNT)])
        acc_set.write({'reconcile': True})
