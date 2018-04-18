# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    final_customer_id = fields.Many2one('res.partner', string='Client Final')
    commission_ids = fields.One2many('commission.commission',
                                     'commission_invoice', 'Commissions')

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """

        res = super(account_invoice, self).action_move_create()
        move_line = self.env['account.move.line']

        for inv in self:
            if not inv.journal_id.sequence_id:
                raise Warning(_('Error!'),
                              _('Please define sequence on the journal \
                                related to this invoice.'))
            if not inv.commission_ids:
                continue

            ctx = dict(self._context, lang=inv.partner_id.lang)

            if not inv.date_invoice:
                inv.with_context(ctx).write(
                    {'date_invoice': fields.Date.context_today(self)})
            date_invoice = inv.date_invoice

            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
            else:
                ref = inv.number

            name = inv.name or inv.supplier_invoice_number or '/'
            journal = inv.journal_id.with_context(ctx)
            if journal.centralisation:
                raise Warning(_('User Error!'),
                              _('You cannot create an invoice on a \
                                centralized journal. Uncheck the centralized \
                                counterpart box in the related journal from \
                                the configuration menu.'))

            # passation des écritures des commissions
            for coms in inv.commission_ids:
                common_vals = {
                    'partner_id': coms.partner_commissioned.id,
                    'debit': 0.0, 'credit': 0.0,
                    'name': name, 'date': date_invoice,
                    'ref': ref, 'quantity': 1.00,
                    'product_id': False, 'product_uom_id': False,
                    'move_id': inv.move_id.id,
                    }
                credit = common_vals.copy()
                debit = common_vals.copy()
                ac = coms.account_commission.id
                acc = coms.account_charge_commission.id
                if coms.account_amount < 0.0:
                    # credit
                    credit['account_id'] = ac
                    credit['debit'] = abs(coms.account_amount)
                    # debit
                    debit['account_id'] = acc
                    debit['credit'] = abs(coms.account_amount)
                else:
                    # credit
                    credit['account_id'] = ac
                    credit['credit'] = abs(coms.account_amount)
                    # debit
                    debit['account_id'] = acc
                    debit['debit'] = abs(coms.account_amount)

                try:
                    move_line.create(debit)
                except Exception, e:
                    raise Warning(
                        _('Error'),
                        _('Can\'t insert value %s in account_move_line debit\n \
                          %s' % (str(debit), e)))
                try:
                    move_line.create(credit)
                except Exception, e:
                    raise Warning(
                        _('Error'),
                        _('Can\'t insert value %s in account_move_line credit\n \
                          %s' % (str(credit), e)))
                ctx['company_id'] = inv.company_id.id
                ctx['invoice'] = inv
                vals = {
                    'move_id': inv.move_id.id,
                }
                coms.with_context(ctx).write(vals)
                inv.move_id.post()
        self._log_event()
        return res

    @api.multi
    def action_cancel(self):
        res = super(account_invoice, self).action_cancel()
        moves = self.env['account.move']
        for inv in self:
            for comm in inv.commission_ids:
                if comm.move_id:
                    moves += comm.move_id

                    for move_line in comm.move_id.line_id:
                        if move_line.reconcile_partial_id.line_partial_ids:
                            raise Warning(_('Error!'),
                                          _('You cannot cancel an invoice \
                                            which is partially paid. You \
                                            need to unreconcile related \
                                            payment entries first.'))
                comm.write({'move_id': False})
        # First, set the invoices as cancelled and detach the move ids
        if moves:
            # second, invalidate the move(s)
            moves.button_cancel()
            # delete the move this invoice was pointing to
            # Note that the corresponding move_lines and move_reconciles
            # will be automatically deleted too
            moves.unlink()
        self._log_event(-1.0, 'Commissions Cancelled')
        return res

    @api.multi
    def recompute_residual(self):
        res = self._compute_residual()
        print("res = %s" % res)
        for coms in self.commission_ids:
            if coms.account_commission.reconcile:
                self.residual -= coms.account_amount
            # self.residual -= sum(self.commission_ids.mapped('account_amount'))
        print("residual = %s" % self.residual)
        return res
