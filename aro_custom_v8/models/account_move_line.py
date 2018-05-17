# -*- coding: utf-8 -*-

from openerp import models, api, fields
import logging
_logger = logging.getLogger(__name__)


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    analytic1 = fields.Char(string='Analytique 1', size=128)
    analytic2 = fields.Char(string='Analytique 2', size=128)
    check_number = fields.Char(string=u'Chèque', size=128)
    # session = fields.Char(string='Session',size=128)
    # piece = fields.Char(string=u'Pièce',size=128)
    # line = fields.Char(string='Ligne',size=128)
    emp_contrat = fields.Char(string='Contrat', size=128)
    emp_police = fields.Char(string='Police', store=True,
                             related='invoice.pol_numpol')
    emp_folio = fields.Char(string='Folio', size=128)
    emp_quittance = fields.Char(string='Quittance', store=True,
                                related='invoice.prm_numero_quittance')
    emp_effet = fields.Date(string='Date Effet', store=True,
                            related="invoice.prm_datedeb")
    emp_emission = fields.Char(string='Emission', size=128)
    emp_unite = fields.Char(string=u'Unité', size=128)
    emp_datfact = fields.Date(string='Date facture', store=True,
                              related="invoice.date_invoice")
    emp_datech = fields.Date(string=u'Date échéance', store=True,
                             related='invoice.prm_datefin')
    emp_libana = fields.Char(string=u'Libellé analytique', size=128)
    emp_fluxtres = fields.Char(string=u'Flux trésorerie', size=128)
    emp_as400_compte = fields.Char(string='AS400 compte', size=128)
    emp_as400_ses = fields.Char(string='AS400 ses')
    emp_as400_pie = fields.Char(string='AS400 pie')
    emp_as400_lig = fields.Char(string='AS400 lig')
    emp_as400_ref = fields.Char(string='AS400 Ref')

    @api.model
    def update_move_line_from_invoice(self):
        period_obj = self.env['account.period']
        period_id = period_obj.search([('code', '=', '01/2016')], limit=100)
        move_line_ids = self.search([('period_id', '=', period_id.id)])
        tmvl = len(move_line_ids)
        i = 0
        for mvl in move_line_ids:
            i += 1
            data = {}
            if not mvl.emp_police:
                data['emp_police'] = mvl.invoice.pol_numpol
            if not mvl.emp_quittance:
                data['emp_quittance'] = mvl.invoice.prm_numero_quittance
            if not mvl.emp_datech:
                data['emp_datech'] = mvl.invoice.prm_datefin
            if not mvl.emp_datfact:
                data['emp_datfact'] = mvl.invoice.date_invoice
            if not mvl.emp_effet:
                data['emp_effet'] = mvl.invoice.prm_datedeb
            mvl.write(data)
            _logger.info('=== %s (%s / %s) ===' % (mvl, i, tmvl))
