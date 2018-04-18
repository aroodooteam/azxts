# -*- coding: utf-8 -*-

from openerp import models, fields, tools
import logging
_logger = logging.getLogger(__name__)


class account_entries_report(models.Model):
    _inherit = "account.entries.report"
    _auto = False

    agency_id = fields.Many2one('base.agency', 'Agence', readonly=True)
    agency_gest_id = fields.Many2one('base.agency', 'Agence Gestion',
                                     readonly=True)

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'account_entries_report')
        cr.execute("""
            create or replace view account_entries_report as (
            select
                l.id as id,
                am.date as date,
                l.date_maturity as date_maturity,
                l.date_created as date_created,
                am.ref as ref,
                am.state as move_state,
                l.state as move_line_state,
                l.reconcile_id as reconcile_id,
                l.partner_id as partner_id,
                l.product_id as product_id,
                l.product_uom_id as product_uom_id,
                am.company_id as company_id,
                am.journal_id as journal_id,
                p.fiscalyear_id as fiscalyear_id,
                am.period_id as period_id,
                l.account_id as account_id,
                l.analytic_account_id as analytic_account_id,
                a.type as type,
                a.user_type as user_type,
                1 as nbr,
                l.quantity as quantity,
                l.currency_id as currency_id,
                l.amount_currency as amount_currency,
                l.debit as debit,
                l.credit as credit,
                coalesce(l.debit, 0.0) - coalesce(l.credit, 0.0) as balance,
                l.agency_id as agency_id,
                ba.parent_id as agency_gest_id
            from
                account_move_line l
                left join account_account a on (l.account_id = a.id)
                left join account_move am on (am.id=l.move_id)
                left join account_period p on (am.period_id=p.id)
                left join base_agency ba on
                   (ba.id = l.agency_id and is_agency_parent is not null)
            where l.state != 'draft'
            )
        """)
        # (l.agency_id = ba.id)
        # ba.parent_id as agency_gest_id
        # ba.is_agency_parent as agency_gest_id
# class account_voucher(models.Model):
#    _inherit = 'account.voucher'

    # journal_id = fields.Many2one('account.journal', 'Journal', required=True,
    # readonly=True, states={'draft':[('readonly',False)]},
    # domain=[('agency_id','=',user.agency_id.id)])
