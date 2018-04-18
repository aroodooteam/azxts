# -*- coding: utf-8 -*-

from openerp import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class account_journal(models.Model):
    _inherit = 'account.journal'

    agency_id = fields.Many2one('base.agency', 'Agence')

    @api.v7
    def false_search(self, cr, uid, args, offset=0, limit=None, order=None,
                     context=None, count=False, xtra=None):
        new_args = []
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        for groups in user.groups_id:
            _logger.info(groups.name)

        for arg in args:
            if type(arg) == list:
                arg = tuple(arg)
            if type(arg) is not tuple:
                new_args += arg
                continue
            else:
                new_args += [arg]
#        if uid!=1:
#            new_args += [('agency_id', '=', user.agency_id.id)]
        return super(account_journal, self).search(cr, uid, new_args, offset,
                                                   limit, order, context,
                                                   count)

    @api.model
    def set_debit_credit_for_opening_journal(self):
        _logger.info('in deb_crd')
        journal_obj = self.env['account.journal']
        account_obj = self.env['account.account']

        domain = [('type', '=', 'situation'), ('centralisation', '=', True)]
        journal_ids = journal_obj.search(domain)
        _logger.info('journal_ids = %s' % journal_ids)

        account_dom = [('code', '=', '468005')]
        account_id = account_obj.search(account_dom).id

        profit_acc_dom = [('code', '=', '774702')]
        profit_acc_id = account_obj.search(profit_acc_dom).id

        loss_acc_dom = [('code', '=', '674702')]
        loss_acc_id = account_obj.search(loss_acc_dom).id

        int_acc_dom = [('code', '=', '580001')]
        int_acc_id = account_obj.search(int_acc_dom).id

        journal_ids.write(
            {
                'default_debit_account_id': account_id,
                'default_credit_account_id': account_id,
                'profit_account_id': profit_acc_id,
                'loss_account_id': loss_acc_id,
                'internal_account_id': int_acc_id,
            })
        _logger.info('End')
