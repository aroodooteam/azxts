# -*- coding: utf-8 -*-

from openerp import models, api
import logging
_logger = logging.getLogger(__name__)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def update_move_line_from_invoice(self):
        aml_obj = self.env['account.move.line']
        invoices = self.search([])
        ttx = len(invoices)
        tto = 0
        for invoice in invoices:
            tto += 1
            _logger.info('=== invoice %s / %s ===' % (tto, ttx))
            line_ids = aml_obj.search([('move_id', '=', invoice.move_id.id)])
            for line_id in line_ids:
                line_id.update({
                    'emp_police': invoice.pol_numpol,
                    'emp_quittance': invoice.prm_numero_quittance,
                    'emp_datech': invoice.prm_datefin,
                    'emp_datfact': invoice.date_invoice,
                    'emp_effet': invoice.prm_datedeb,
                })
