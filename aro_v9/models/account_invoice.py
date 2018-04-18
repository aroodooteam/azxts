# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    amendment_line_id = fields.Many2one(comodel_name='aro.amendment.line', string='History')
    subscription_id = fields.Many2one(comodel_name='aro.insurance.subscription', string='Subscription', related='amendment_line_id.subscription_id')

    @api.model
    def create(self, vals):
        logger.info('\n *-*-* ctx = %s' % self._context)
        amendment_line_obj = self.env['aro.amendment.line']
        res = super(AccountInvoice, self).create(vals)
        amendment_line = self._context.get('default_amendment_line_id', False)
        if amendment_line:
            amendment_line_id = amendment_line_obj.browse(amendment_line)
            amendment_line_id.write({'invoice_id': res.id})
            res.button_reset_taxes()
        return res

