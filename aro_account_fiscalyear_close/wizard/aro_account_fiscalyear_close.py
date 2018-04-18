# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)



class AroAccountFiscalyearClose(models.TransientModel):
    _name = 'aro.account.fiscalyear.close'
    _description = 'Redefine closing fiscalyear by agency'

    @api.multi
    def _get_journals(self):
        journal_obj = self.env['account.journal']
        return journal_obj.search([('type','=','situation'), ('centralisation', '=', True)])

    @api.multi
    def _get_specified_account_agency(self):
        """
        This function set all record in restricted_account_agency
        to the wizard
        """
        raa_obj = self.env['restricted.account.agency']
        return raa_obj.search([])

    @api.multi
    def _get_account_to_group(self):
        acc_obj = self.env['account.account']
        dom = [
            ('code', '!=', '466500'), ('type', '=', 'other'),
            '|', '|', '|', '|', '|', ('code', 'ilike', '233%'), ('code', 'ilike', '251%'),
            ('code', 'ilike', '40%'), ('code', 'ilike', '411%'), ('code', 'ilike', '42%'),
            ('code', 'ilike', '466%')
        ]
        acc_ids = acc_obj.search(dom)
        logger.info('\n=== acc_gp_ids = %s' % acc_ids)
        return acc_ids

    fy_to_close_id = fields.Many2one(
        comodel_name='account.fiscalyear', string='Fiscal year to close',
        required=True)
    fy_to_open_id = fields.Many2one(
        comodel_name='account.fiscalyear', string='Fiscal year to open',
        required=True)
    period_to_open_id = fields.Many2one(
        comodel_name='account.period', string='Period', required=True,
        help='Period to put opening entries')
    report_name = fields.Char(
        string='Description for new entries', required=True,
        help='Description for opening entries')
    journal_ids = fields.Many2many(
        comodel_name='account.journal', string='Journals', required=True,
        domain="[('type','=','situation'), ('centralisation', '=', True)]",
        help='List of journal to contain opening entries',
        default=_get_journals
    )
    restricted_acc_ids = fields.Many2many(
        comodel_name='restricted.account.agency',
        string='Restricted Account Agency',
        default=_get_specified_account_agency
    )
    account_gp_ids = fields.Many2many(
        comodel_name='account.account',
        string='Account',
        default=_get_account_to_group,
        help='Account grouped by partner')

    _defaults = {
        'report_name': lambda self, cr, uid, context: _('End of Fiscal Year Entry'),
    }

    @api.multi
    def get_special_account(self, account_ids, agency):
        """
        remove special account for other agency
        and return the rest
        account_ids: recordset of account.account
        agency: record of base.agency
        """
        ra_list = self.env['restricted.account.agency']
        for ra_id in self.restricted_acc_ids:
            if ra_id.name.id == agency.id:
                ra_list += ra_id
            # if ra_id.name.id != agency.id:
            #     ra_list += ra_id
        # logger.info('ra_list = %s' % ra_list)
        ra_acc = ra_list.mapped('account_ids')
        # logger.info('ra_acc = %s' % ra_acc)
        # final_acc = account_ids - ra_acc
        intersect_acc = False
        if ra_acc:
            intersect_acc = ra_acc & account_ids
        # else:
        #     intersect_acc = account_ids
        # logger.info('final_acc = %s' % final_acc)
        return intersect_acc

    @api.multi
    def data_save(self):
        """
        This function close account fiscalyear and create entries in new fiscalyear by agency
        """
        self.ensure_one()
        # init model to use
        period_obj = self.env['account.period']
        fy_obj = self.env['account.fiscalyear']
        journal_obj = self.env['account.journal']
        move_obj = self.env['account.move']
        ml_obj = self.env['account.move.line']
        account_obj = self.env['account.account']
        acc_jrn_period_obj = self.env['account.journal.period']
        currency_obj = self.env['res.currency']
        account_type_obj = self.env['account.account.type']
        agency_obj = self.env['base.agency']

        # TODO
        def _reconcile_fy_closing(move_line_ids):
            logger.info('\n=== mvl_ids to reconcile = %s' % len(move_line_ids))
            # check if account_move_line is for one company
            if len(move_line_ids.mapped('company_id')) > 1:
                raise exceptions.Warning(_('The entries to reconcile should belong to the same company.'))
            # create move_reconcile to reconcile move_line_ids
            r_id = self.env['account.move.reconcile'].create({'type': 'auto', 'opening_reconciliation': True})
            logger.info('\n=== r_id = %s ===' % r_id)
            # move_line_ids.write({'reconcile_id': r_id.id})
            self._cr.execute('update account_move_line set reconcile_id = %s where id in %s',(r_id.id, tuple(move_line_ids.ids)))
            logger.info('\n=== end r_id = %s ===' % r_id)

            # reconcile_ref depends from reconcile_id but was not recomputed
            move_line_ids._store_set_values(['reconcile_ref'])
            move_line_ids.invalidate_cache()
            logger.info('\n=== fin reconcile_fy_closing ===')
            return r_id


        fyc = self.fy_to_close_id.id
        # fyc_period = period_obj.search([('fiscalyear_id', '=', fyc)])
        # fy_period_set = fyc_period
        fyc_period = period_obj.search([('date_stop', '<', self.fy_to_open_id.date_start)])
        fyo = self.fy_to_open_id.id

        # get all period to use to generate new opening entries
        # fy2_period_set = fyo_period
        fyo_period = period_obj.search([('fiscalyear_id', '=', fyo)])

        if not fyc_period or not fyo_period:
            raise exceptions.Warning(_('The periods to generate opening entries cannot be found.'))
        period = self.period_to_open_id
        new_fyear = self.fy_to_open_id
        old_fyear = self.fy_to_close_id

        # get list of journal for opening entries by agency
        journal_ids = self.journal_ids
        logger.info('journal_ids = %s' % journal_ids)
        company_ids = 1

        # check debit and credit account on each journal
        logger.info('Checking all journal start')
        for journal in self.journal_ids:
            if not journal.default_credit_account_id or not journal.default_debit_account_id:
                raise exceptions.Warning(
                    _('The journal %s must have default credit and debit account.' % journal.name))
            if (not journal.centralisation) or journal.entry_posted:
                raise exceptions.Warning(
                    _('The journal %s must have centralized counterpart without the Skipping draft state option checked.' % journal.name))
        logger.info('Checking all journal end')

        # delete existing move and move lines if any
        # in new opening journal and period
        logger.info('Start deleting move and move_line')
        mv_doms = [('journal_id', 'in', journal_ids.ids),
                   ('period_id', '=', period.id)]
        move_ids = move_obj.search(mv_doms)
        logger.info('move_ids = %s' % move_ids)
        logger.info('move_ids_len = %s' % len(move_ids))
        # TODO
        if move_ids:
            mvl_ids = ml_obj.search([('move_id', 'in', move_ids.ids)])
            mvl_ids._remove_move_reconcile(opening_reconciliation=True)
            # obj_acc_move_line._remove_move_reconcile(cr, uid, move_line_ids, opening_reconciliation=True, context=context)
            mvl_ids.unlink()
            move_ids.unlink()
        logger.info('End deleting move and move_line')

        # TODO
        # Query line
        self._cr.execute("SELECT id FROM account_fiscalyear WHERE date_stop < %s", (str(new_fyear.date_start),))
        result = self._cr.dictfetchall()
        # logger.info('\n===result = %s' % result)
        fy_ids = [x['id'] for x in result]
        # period_list = period_obj.search([('fiscalyear_id', 'in', fy_ids)])
        logger.info('fy_ids = %s' % fy_ids)
        ctx = self._context.copy()
        ctx.update({'fiscalyear': fy_ids})
        query_line = ml_obj.with_context(ctx)._query_get(
                obj='account_move_line')
        """
        query_line = account_move_line.state <> 'draft' AND
        account_move_line.period_id IN (SELECT id FROM account_period WHERE fiscalyear_id IN (2, 3))
        """
        logger.info('query_line = %s' % query_line)

        len_jrn = len(self.journal_ids)
        len_jr = 0
        # create the opening move for each journals
        #1. report of the accounts with defferal method == 'unreconciled'
        domain_acc_unreconciled = [
            ('active', '=', True),
            ('type', 'not in', ('view', 'consolidation')),
            ('user_type.close_method', '=', 'unreconciled')
        ]
        account_ids_unreconciled = account_obj.search(domain_acc_unreconciled)
        logger.info('#1 account_ids_unreconciled = %s' % account_ids_unreconciled)
        #2. report of the accounts with defferal method == 'detail'
        domain_acc_detail = [
            ('active', '=', True),
            ('type', 'not in', ('view', 'consolidation')),
            ('user_type.close_method', '=', 'detail')
        ]
        account_ids_detail = account_obj.search(domain_acc_detail)
        logger.info('#2 account_ids_detail= %s' % account_ids_detail)
        #3. report of the accounts with defferal method == 'balance'
        domain_acc_balance = [
            ('active', '=', True),
            ('type', 'not in', ('view', 'consolidation')),
            ('user_type.close_method', '=', 'balance')
        ]
        account_ids_balance = account_obj.search(domain_acc_balance)
        logger.info('#3 account_ids_balance = %s' % len(account_ids_balance))

        #4. report of the accounts with defferal method == 'balance' grouped by partner
        logger.info('#4 account_gp_ids = %s' % self.account_gp_ids)
        account_ids_balance_new = account_ids_balance - self.account_gp_ids
        logger.info('#5 account_ids_balance_new = %s' % len(account_ids_balance_new))
        # ================== End getting accounts ==================
        # => get all fiscalyear after the fyc
        fyx_ids = fy_obj.search([('date_start', '>', self.fy_to_close_id.date_stop)])
        # <=
        # => get period list without opening period of all next fy
        period_fyx_ids = period_obj.search([('fiscalyear_id', 'in', fyx_ids.ids), ('code', 'not ilike', '00/%')])
        logger.info('\n=== period_fyx_ids = %s' % period_fyx_ids)
        # <=
        # Start loop on journal_ids ==========================================
        for journal in self.journal_ids:
            len_jr += 1
            logger.info('\n=== %s / %s => %s' % (len_jr, len_jrn, journal.name))
            vals = {
                'name': _('Opening entries %s - %s' % (period.code.split('/')[1], journal.agency_id.name)),
                'ref': '',
                'period_id': period.id,
                'date': period.date_start,
                'journal_id': journal.id,
            }
            move_id = move_obj.create(vals)
            logger.info('move_id = %s' % move_id)

            # 1. report of the accounts with defferal method == 'unreconciled'
            # acc_type_dom = [('close_method', '=', 'unreconciled')]
            # acc_type_ids = account_type_obj.search(acc_type_dom)

            # ('user_type.close_method', 'in', acc_type_ids.ids)
            # TODO
            # account_ids = account_ids_unreconciled
            # Disable this this line if u doesn't need make filter by account and agency
            account_ids = self.get_special_account(account_ids_unreconciled, journal.agency_id)

            #-------------------------------------------------------
            ag_ids = agency_obj.search([('have_opening_journal', '=', False), ('parent_id', '=', journal.agency_id.id)])
            logger.info('Agence gerer par %s => %s' % (journal.agency_id.name,ag_ids.mapped('name')))
            if account_ids:
                logger.info('unreconciled account_ids for %s => %s' % (journal.agency_id.name,account_ids.mapped('name')))
                # search all move_line that should be inserted in this move
                # get move_line corresponding directly with agency in journal
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                      (SELECT account_move_line.name, account_move_line.create_uid, account_move_line.create_date, account_move_line.write_uid, account_move_line.write_date,
                         account_move_line.statement_id, %s,account_move_line.currency_id, account_move_line.date_maturity, account_move_line.partner_id,
                         account_move_line.blocked, account_move_line.credit, 'draft', account_move_line.debit, account_move_line.ref, account_move_line.account_id,
                         %s, (%s) AS date, %s, account_move_line.amount_currency, account_move_line.quantity, account_move_line.product_id, account_move_line.company_id, account_move_line.agency_id, account_move_line.emp_police, account_move_line.emp_quittance, account_move_line.emp_effet, account_move_line.emp_as400_compte,
                         account_move_line.emp_as400_pie, account_move_line.emp_as400_ses, account_move_line.emp_as400_lig, account_move_line.emp_fluxtres, account_move_line.emp_libana
                       FROM account_move_line
                             left join base_agency ba on ba.id = account_move_line.agency_id
                             left join account_journal aj on (aj.agency_id = ba.id and account_move_line.journal_id = aj.id)
                       WHERE account_id IN %s
                         AND ''' + query_line + '''
                         AND account_move_line.reconcile_id IS NULL
                         AND ba.id = %s
                                )''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), journal.agency_id.id))

                # get move_line unreconciled from other agency
                # left join account_journal aj on aj.agency_id = ba.id
                # AND aml.journal_id = aj.id
                for ag_id in ag_ids:
                    self._cr.execute('''
                        INSERT INTO account_move_line (
                             name, create_uid, create_date, write_uid, write_date,
                             statement_id, journal_id, currency_id, date_maturity,
                             partner_id, blocked, credit, state, debit,
                             ref, account_id, period_id, date, move_id, amount_currency,
                             quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                          (SELECT account_move_line.name, account_move_line.create_uid, account_move_line.create_date, account_move_line.write_uid, account_move_line.write_date,
                             account_move_line.statement_id, %s,account_move_line.currency_id, account_move_line.date_maturity, account_move_line.partner_id,
                             account_move_line.blocked, account_move_line.credit, 'draft', account_move_line.debit, account_move_line.ref, account_move_line.account_id,
                             %s, (%s) AS date, %s, account_move_line.amount_currency, account_move_line.quantity, account_move_line.product_id, account_move_line.company_id, account_move_line.agency_id, account_move_line.emp_police, account_move_line.emp_quittance, account_move_line.emp_effet, account_move_line.emp_as400_compte,
                         account_move_line.emp_as400_pie, account_move_line.emp_as400_ses, account_move_line.emp_as400_lig, account_move_line.emp_fluxtres, account_move_line.emp_libana

                           FROM account_move_line
                                 left join base_agency ba on ba.id = account_move_line.agency_id
                                 left join account_journal aj on (aj.agency_id = ba.id and account_move_line.journal_id = aj.id)
                           WHERE account_id IN %s
                             AND ''' + query_line + '''
                             AND account_move_line.reconcile_id IS NULL
                             AND ba.id = %s
                                    )''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), ag_id.id))

                #We have also to consider all move_lines that were reconciled
                #on another fiscal year, and report them too
                # logger.info('fyo_period = %s' % str(tuple(fyo_period.ids)) )
                # logger.info('fyc_period = %s' % str(tuple(fyc_period.ids)) )
                # left join account_journal aj on aj.agency_id = ba.id
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                      (SELECT
                         b.name, b.create_uid, b.create_date, b.write_uid, b.write_date,
                         b.statement_id, %s, b.currency_id, b.date_maturity,
                         b.partner_id, b.blocked, b.credit, 'draft', b.debit,
                         b.ref, b.account_id, %s, (%s) AS date, %s, b.amount_currency,
                         b.quantity, b.product_id, b.company_id, b.agency_id, b.emp_police, b.emp_quittance, b.emp_effet, b.emp_as400_compte,
                         b.emp_as400_pie, b.emp_as400_ses, b.emp_as400_lig, b.emp_fluxtres, b.emp_libana
                         FROM account_move_line b
                             left join base_agency ba on ba.id = b.agency_id
                             left join account_journal aj on (aj.agency_id = ba.id and b.journal_id = aj.id)
                         WHERE b.account_id IN %s
                           AND b.reconcile_id IS NOT NULL
                           AND b.period_id IN ''' + str(tuple(fyc_period.ids)) + \
                         '''
                           AND ba.id = %s
                           AND b.reconcile_id IN (SELECT DISTINCT(reconcile_id)
                                              FROM account_move_line a
                                              WHERE a.period_id IN '''+str(tuple(period_fyx_ids.ids))+'''))''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), journal.agency_id.id))
                self.invalidate_cache()
                for ag_id in ag_ids:
                    self._cr.execute('''
                        INSERT INTO account_move_line (
                             name, create_uid, create_date, write_uid, write_date,
                             statement_id, journal_id, currency_id, date_maturity,
                             partner_id, blocked, credit, state, debit,
                             ref, account_id, period_id, date, move_id, amount_currency,
                             quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                          (SELECT
                             b.name, b.create_uid, b.create_date, b.write_uid, b.write_date,
                             b.statement_id, %s, b.currency_id, b.date_maturity,
                             b.partner_id, b.blocked, b.credit, 'draft', b.debit,
                             b.ref, b.account_id, %s, (%s) AS date, %s, b.amount_currency,
                             b.quantity, b.product_id, b.company_id, b.agency_id, b.emp_police, b.emp_quittance, b.emp_effet, b.emp_as400_compte,
                         b.emp_as400_pie, b.emp_as400_ses, b.emp_as400_lig, b.emp_fluxtres, b.emp_libana
                             FROM account_move_line b
                                 left join base_agency ba on ba.id = b.agency_id
                                 left join account_journal aj on (aj.agency_id = ba.id and b.journal_id = aj.id)
                             WHERE b.account_id IN %s
                               AND b.reconcile_id IS NOT NULL
                               AND b.period_id IN ''' + str(tuple(fyc_period.ids)) + \
                             '''
                               AND ba.id = %s
                               AND b.reconcile_id IN (SELECT DISTINCT(reconcile_id)
                                                  FROM account_move_line a
                                                  WHERE a.period_id IN '''+str(tuple(period_fyx_ids.ids))+'''))''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), ag_id.id))

                    self.invalidate_cache()
            # ================================================================
            #2. report of the accounts with defferal method == 'detail'
            # account_ids = account_ids_detail
            logger.info('Detail account_ids = %s' % account_ids_detail)
            # TODO
            # account_ids = account_ids_detail
            # Disable this this line if u doesn't need make filter by account and agency
            account_ids = self.get_special_account(account_ids_detail, journal.agency_id)
            logger.info('detail account_ids = %s' % account_ids)
            if account_ids:
                self._cr.execute('''
                    INSERT INTO account_move_line (
                         name, create_uid, create_date, write_uid, write_date,
                         statement_id, journal_id, currency_id, date_maturity,
                         partner_id, blocked, credit, state, debit,
                         ref, account_id, period_id, date, move_id, amount_currency,
                         quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                      (SELECT account_move_line.name, account_move_line.create_uid, account_move_line.create_date, account_move_line.write_uid, account_move_line.write_date,
                         account_move_line.statement_id, %s,account_move_line.currency_id, account_move_line.date_maturity, account_move_line.partner_id,
                         account_move_line.blocked, account_move_line.credit, 'draft', account_move_line.debit, account_move_line.ref, account_move_line.account_id,
                         %s, (%s) AS date, %s, account_move_line.amount_currency, account_move_line.quantity, account_move_line.product_id, account_move_line.company_id,account_move_line.agency_id, account_move_line.emp_police, account_move_line.emp_quittance, account_move_line.emp_effet, account_move_line.emp_as400_compte,
                         account_move_line.emp_as400_pie, account_move_line.emp_as400_ses, account_move_line.emp_as400_lig, account_move_line.emp_fluxtres, account_move_line.emp_libana
                       FROM account_move_line
                             left join base_agency ba on ba.id = account_move_line.agency_id
                             left join account_journal aj on aj.agency_id = ba.id
                       WHERE account_id IN %s
                         AND ''' + query_line + '''
                         AND reconcile_id IS NULL
                         AND ba.id = %s
                         AND account_move_line.journal_id = aj.id
                                )''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), journal.agency_id.id))
                self.invalidate_cache()
                for ag_id in ag_ids:
                    self._cr.execute('''
                        INSERT INTO account_move_line (
                             name, create_uid, create_date, write_uid, write_date,
                             statement_id, journal_id, currency_id, date_maturity,
                             partner_id, blocked, credit, state, debit,
                             ref, account_id, period_id, date, move_id, amount_currency,
                             quantity, product_id, company_id, agency_id, emp_police, emp_quittance, emp_effet, emp_as400_compte,
                         emp_as400_pie, emp_as400_ses, emp_as400_lig, emp_fluxtres, emp_libana)
                          (SELECT account_move_line.name, account_move_line.create_uid, account_move_line.create_date, account_move_line.write_uid, account_move_line.write_date,
                             account_move_line.statement_id, %s,account_move_line.currency_id, account_move_line.date_maturity, account_move_line.partner_id,
                             account_move_line.blocked, account_move_line.credit, 'draft', account_move_line.debit, account_move_line.ref, account_move_line.account_id,
                             %s, (%s) AS date, %s, account_move_line.amount_currency, account_move_line.quantity, account_move_line.product_id, account_move_line.company_id,account_move_line.agency_id, account_move_line.emp_police, account_move_line.emp_quittance, account_move_line.emp_effet, account_move_line.emp_as400_compte,
                         account_move_line.emp_as400_pie, account_move_line.emp_as400_ses, account_move_line.emp_as400_lig, account_move_line.emp_fluxtres, account_move_line.emp_libana
                           FROM account_move_line
                                 left join base_agency ba on ba.id = account_move_line.agency_id
                                 left join account_journal aj on aj.agency_id = ba.id
                           WHERE account_id IN %s
                             AND ''' + query_line + '''
                             AND reconcile_id IS NULL
                             AND ba.id = %s
                             AND account_move_line.journal_id = aj.id
                                    )''', (journal.id, period.id, period.date_start, move_id.id, tuple(account_ids.ids), ag_id.id))
                    self.invalidate_cache()
            # ================================================================
            #3. report of the accounts with defferal method == 'balance'
            # account_ids = account_ids_balance
            # logger.info('account_ids#3 = %s' % account_ids.mapped('code'))
            logger.info('Balance account_ids # 1 = %s' % len(account_ids_balance))
            # TODO
            # account_ids = account_ids_balance
            # Disable this this line if u doesn't need make filter by account and agency
            account_ids = self.get_special_account(account_ids_balance, journal.agency_id)
            account_ids_gpd = self.get_special_account(self.account_gp_ids, journal.agency_id)
            # account_ids = account_ids - self.account_gp_ids # remove account will be grouped by partner
            if not account_ids:
                logger.info('\n=== no account_ids balance')
                continue
            logger.info('Balance account_ids # 2 = %s' % len(account_ids))
            # split query
            query_1st_part = """
                    INSERT INTO account_move_line (
                         debit, credit, name, date, move_id, journal_id, period_id,
                         account_id, currency_id, amount_currency, company_id, state, agency_id, partner_id) VALUES
            """
            query_2nd_part = ""
            query_2nd_part_args = []

            agency_list = []
            agency_list.append(journal.agency_id.id)
            if ag_ids:
                agency_list += ag_ids.ids
            # else:
            #     agency_list.append(journal.agency_id.id)
            # search account_move_line contain the agency and the account with the period
            dom_balance = [
                ('period_id', 'in', fyc_period.ids),('account_id', 'in', account_ids.ids),
                ('agency_id', 'in', agency_list)
            ]
            logger.info('dom_balance = %s' % dom_balance)
            ml_balance = ml_obj.search(dom_balance)
            logger.info('move_line balance account = %s' % len(ml_balance))
            # This part remove all the opening period from list of period
            period_without_opening = """
                select id from account_period where id in %s and %s
            """ % (tuple(fyc_period.ids),"code not like '00/%';")
            self._cr.execute(period_without_opening)
            period_result = self._cr.dictfetchall()
            balance_fy_ids = [x['id'] for x in period_result]
            # End of recompute period for balance account
            if ml_balance:
                for account in account_ids:
                    logger.info('account_balance %s %s => %s' % (account.code, account.name, account.balance))
                    # # recherche des balances (montants) par agence pour un compte
                    # # journal, agence, compte
                    # # logger.info('agency_list = %s' % agency_list)
                    # ml_obj_acc_dom = [
                    #     ('account_id', '=', account.id),
                    #     ('journal_id.agency_id', 'in', agency_list),
                    # ]
                    # # ('period_id.code', 'not like', '00/%')
                    # # logger.info('ml_obj_acc = %s' % ml_obj_acc_dom)
                    # ml_acc_ag_ids = ml_obj.search(ml_obj_acc_dom)
                    # agency_account_balance = ml_acc_ag_ids.get_agency_account_balance()
                    # balance = agency_account_balance.get('balance')
                    # if balance != 0:
                    #     logger.info('agency_account_balance = %s' % agency_account_balance)
                    # get balance by agency
                    balance_sql = """
                    select
                        aa.code,aa.name as acc_name,
                        coalesce(sum(aml.debit),0) as debit,
                        coalesce(sum(aml.credit),0) as credit,
                        coalesce(sum(aml.debit)) - coalesce(sum(aml.credit)) as balance,
                        (select case when currency_id IS NULL THEN 0 ELSE COALESCE(SUM(aml.amount_currency),0) END FROM account_account WHERE id in (aml.account_id)) as foreign_balance
                    from account_move_line aml
                    left join account_account aa on aa.id=aml.account_id
                    left join base_agency ba on ba.id=aml.agency_id
                    where aml.period_id in %s and aml.account_id=%s and aml.agency_id in %s
                    group by aa.code,aa.name,aml.account_id;
                    """
                    if account in account_ids_gpd:
                        logger.info('\n === account gp = %s' % account.code)
                        balance_sql = """
                        select
                            aml.partner_id,aa.code,aa.name as acc_name,
                            coalesce(sum(aml.debit),0) as debit,
                            coalesce(sum(aml.credit),0) as credit,
                            coalesce(sum(aml.debit)) - coalesce(sum(aml.credit)) as balance,
                            (select case when currency_id IS NULL THEN 0 ELSE COALESCE(SUM(aml.amount_currency),0) END FROM account_account WHERE id in (aml.account_id)) as foreign_balance
                        from account_move_line aml
                        left join account_account aa on aa.id=aml.account_id
                        left join base_agency ba on ba.id=aml.agency_id
                        where aml.period_id in %s and aml.account_id=%s and aml.agency_id in %s
                        group by aa.code,aa.name,aml.account_id,aml.partner_id;
                        """

                    # param_balance_sql = (
                    #     tuple(fyc_period.ids), account.id, tuple(agency_list)
                    # )
                    param_balance_sql = (
                        tuple(balance_fy_ids), account.id, tuple(agency_list)
                    )
                    self._cr.execute(balance_sql, tuple(param_balance_sql))
                    balance_result = self._cr.dictfetchall()
                    logger.info('balance_result = %s' % balance_result)
                    balance = 0
                    credit = 0
                    debit = 0
                    foreign_balance = 0
                    partner_id = None
                    company_currency_id = self.env['res.users'].browse(self._uid).company_id.currency_id
                    for balance_res in balance_result:
                        balance = balance_res.get('balance')
                        credit = balance_res.get('credit')
                        debit = balance_res.get('debit')
                        foreign_balance = balance_res.get('foreign_balance')
                        partner_id = balance_res.get('partner_id', None)
                        # if not currency_obj.is_zero(cr, uid, company_currency_id, abs(account.balance)):
                        if not company_currency_id.is_zero(abs(balance)):
                            if query_2nd_part:
                                query_2nd_part += ','
                            query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                            # query_2nd_part_args += (balance > 0 and balance or 0.0,
                            #         balance < 0 and -balance or 0.0,
                            query_2nd_part_args += (balance > 0 and balance or 0.0,
                                   balance < 0 and -balance or 0.0,
                                   self.report_name,
                                   period.date_start,
                                   move_id.id,
                                   journal.id,
                                   period.id,
                                   account.id,
                                   account.currency_id and account.currency_id.id or None,
                                   foreign_balance if account.currency_id else 0.0,
                                   account.company_id.id,
                                   'draft',
                                   journal.agency_id.id,
                                   partner_id)
                    # ==================================================
                    #- if balance_result:
                    #-     balance = balance_result[0].get('balance')
                    #-     credit = balance_result[0].get('credit')
                    #-     debit = balance_result[0].get('debit')
                    #-     foreign_balance = balance_result[0].get('foreign_balance')
                    #-     partner_id = balance_result[0].get('partner_id', None)
                    #- # if not currency_obj.is_zero(cr, uid, company_currency_id, abs(account.balance)):
                    #- if not company_currency_id.is_zero(abs(balance)):
                    #-     if query_2nd_part:
                    #-         query_2nd_part += ','
                    #-     query_2nd_part += "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
                    #-     # query_2nd_part_args += (balance > 0 and balance or 0.0,
                    #-     #         balance < 0 and -balance or 0.0,
                    #-     query_2nd_part_args += (balance > 0 and balance or 0.0,
                    #-            balance < 0 and -balance or 0.0,
                    #-            self.report_name,
                    #-            period.date_start,
                    #-            move_id.id,
                    #-            journal.id,
                    #-            period.id,
                    #-            account.id,
                    #-            account.currency_id and account.currency_id.id or None,
                    #-            foreign_balance if account.currency_id else 0.0,
                    #-            account.company_id.id,
                    #-            'draft',
                    #-            journal.agency_id.id,
                    #-            partner_id)
                if query_2nd_part:
                    logger.info('Insert move_line account balance')
                    self._cr.execute(query_1st_part + query_2nd_part, tuple(query_2nd_part_args))
                    self.invalidate_cache()

            # ================================================================
            #validate and centralize the opening move
            move_id.validate()
            logger.info('\n=== fin journal %s' % journal.name)

        # End loop on journal_ids ============================================
        # TODO
        #reconcile all the move.line of the opening move
        logger.info('\n=== Start reconcile all move.line of the opening move ===')
        ml_rcl_dom = [('journal_id', 'in', self.journal_ids.ids), ('period_id.fiscalyear_id', '=', fyo)]
        new_ml_ids = ml_obj.search(ml_rcl_dom)
        if new_ml_ids:
            reconcile_id = _reconcile_fy_closing(new_ml_ids)
            #set the creation date of the reconcilation at the first day of the new fiscalyear, in order to have good figures in the aged trial balance
            # reconcile_id = self.env['account.move.reconcile'].browse(reconcile_id)
            reconcile_id.write({'create_date': new_fyear.date_start})
        logger.info('\n>>> End reconcile all move.line of the opening move ===')

        logger.info('\n=== CARE ===')
        len_jr = 0
        # TODO CARE
        # create the journal.period object and link it to the old fiscalyear
        new_period = self.period_to_open_id.id
        for jrn_id in self.journal_ids:
            len_jr += 1
            logger.info('=== care %s / %s => %s' % (len_jr, len_jrn, journal.name))
            acc_jrn_ids = acc_jrn_period_obj.search([('journal_id', '=', jrn_id.id), ('period_id', '=', new_period)])
            if not acc_jrn_ids:
                acc_jrn_ids = [acc_jrn_period_obj.create({
                       'name': (jrn_id.name or '') + ':' + (period.code or ''),
                       'journal_id': jrn_id.id,
                       'period_id': period.id
                   }).id]
            else:
                acc_jrn_ids = acc_jrn_ids.ids
            logger.info('=== acc_jrn_ids = %s' % acc_jrn_ids)
            self._cr.execute('UPDATE account_fiscalyear ' \
                        'SET end_journal_period_id = %s ' \
                        'WHERE id = %s', (acc_jrn_ids[0], old_fyear.id))
            fy_obj.invalidate_cache(['end_journal_period_id'], [old_fyear.id])
        logger.info('\n=== End generate opening entries')
        return {'type': 'ir.actions.act_window_close'}
