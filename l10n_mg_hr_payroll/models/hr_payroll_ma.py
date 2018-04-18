# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
import StringIO
import base64
import calendar
import xlwt
import string
import calendar
import logging

_logger = logging.getLogger(__name__)

class hr_payroll_ma(osv.osv):

    def _get_journal(self, cr, uid, context):
        if context is None:
            context = {}
        journal_obj = self.pool.get('account.journal')
        res = journal_obj.search(cr, uid, [('name', '=', 'journal des salaires')], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_currency(self, cr, uid, context):
        if context is None:
            context = {}
        currency_obj = self.pool.get('res.currency')
        res = currency_obj.search(cr, uid, [('symbol', '=', 'MAD')], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_partner(self, cr, uid, data, context={}):
        company_obj = self.pool.get('res.company')
        ids_company = company_obj.search(cr, uid, [])
        res = company_obj.read(cr, uid, ids_company[0])
        if res:
            return res['partner_id'][0]
        else:
            return False

    def _total_net(self, cr, uid, ids, name, arg, context={}):
        result = {}
        for payroll in self.browse(cr, uid, ids, context):
            net = 0
            for line in payroll.bulletin_line_ids:
                net += line.salaire_net_a_payer
            result[payroll.id] = net
        return result

    _name = "hr.payroll_ma"
    _description = 'Saisie des bulletins'
    _order = "number"
    _columns = {
        'name': fields.char('Description', size=64),
        'number': fields.char('Numero du salaire', size=32, readonly=True),
        'date_transfer': fields.date('Date transfert', states={'open':[('readonly', True)], 'close':[('readonly', True)]}, select=1),
        'date_salary': fields.date('Date salaire', states={'open':[('readonly', True)], 'close':[('readonly', True)]}, select=1),
        'partner_id': fields.many2one('res.partner', 'Employeur', change_default=True, readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
        'period_id': fields.many2one('account.period', 'Periode', domain=[('state', '<>', 'done')], readonly=True, required=True, states={'draft':[('readonly', False)]}, select=1),
        'bulletin_line_ids': fields.one2many('hr.payroll_ma.bulletin', 'id_payroll_ma', 'Bulletins', readonly=True, states={'draft':[('readonly', False)]}),
        'move_id': fields.many2one('account.move', 'salary Movement', readonly=True, help="Link to the automatically generated account moves."),
        'currency_id': fields.many2one('res.currency', 'Devise', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'journal_id': fields.many2one('account.journal', 'Journal', required=True, readonly=True, states={'draft':[('readonly', False)]}),
        'bank_id': fields.many2one('res.partner.bank', 'Banque', readonly=True, states={'draft':[('readonly', False)]}),
        'state': fields.selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirme'),
            ('paid', 'Done'),
            ('cancelled', 'Cancelled')
        ], 'State', select=2, readonly=True),
        'total_net': fields.function(_total_net, method=True, type='float', digits=(16, 2), string='Total net'),
        }
    def _name_get_default(self, cr, uid, context=None):
            return self.pool.get('ir.sequence').get(cr, uid, 'hr.payroll_ma')
    _defaults = {
        'number': _name_get_default,
        'date_salary': lambda * a: time.strftime('%Y-%m-%d'),
        'state': lambda * a: 'draft',
        'journal_id': _get_journal,
        'partner_id': _get_partner,
        'currency_id': _get_currency,

    }
    def _check_unicite(self, cr, uid, ids):
           for unicite in self.browse(cr, uid, ids):
               unicite_id = self.search(cr, uid, [('period_id', '=', int(unicite.period_id)), ('partner_id', '=', int(unicite.partner_id)) ])
               if len(unicite_id) > 1:
                   return False
           return True

    _constraints = [
        (_check_unicite, u'Cette période éxiste déjà', ['period'])
        ]

    def onchange_period_id(self, cr, uid, ids, period_id, partner_id):
        partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
        period = self.pool.get('account.period').browse(cr, uid, period_id)

        result = {'value': {
                            'name' :   'Salaires %s de la periode %s' % (partner.name, period.name),
                            }
                    }

        return result

    def draft_cb(self, cr, uid, ids, context=None):
        for sal in self.browse(cr, uid, ids):
            if sal.move_id:
                raise osv.except_osv(_('Error !'), _(u'Veuillez d\'abord supprimer les écritures comptables associés'))

        return self.write(cr, uid, ids, {'state':'draft'}, context=context)

    def confirm_cb(self, cr, uid, ids, context=None):
        self.action_move_create(cr, uid, ids)
        return self.write(cr, uid, ids, {'state':'confirmed'}, context=context)

    def cancel_cb(self, cr, uid, ids, context=None):
        return self.write(cr, uid, ids, {'state':'cancelled'}, context=context)

    def create_reports(self, cr, uid, ids, context=None):
        created = []
        for id in self.create_legal_reports(cr, uid, ids):
            created.append(id)
        for id in self.action_bank_file_create(cr, uid, ids):
            created.append(id)
        for id in self.create_pay_journal(cr, uid, ids):
            created.append(id)

        return {
            'type': 'ir.actions.act_window',
            'name': 'Rapports RH',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': context,
            'domain' : [('id', 'in', created)],
            'res_model': 'ir.attachment',
            'nodestroy': True,
        }

    def create_pay_journal(self, cr, uid, ids, context=None):
        fiscalyear_obj = self.pool.get('account.fiscalyear')
        company_obj = self.pool.get('res.company')
        ids_company = company_obj.search(cr, uid, [])
        dictionnaire = company_obj.read(cr, uid, ids_company[0])
        proxy = self.pool.get('hr.payroll_ma')
        bulletin_obj = self.pool.get('hr.payroll_ma.bulletin')

        objects = proxy.browse(cr, uid, ids, context=context)
        attach_id = []
        for object in objects:
            period_id = object.period_id.id
            bulletins = bulletin_obj.search(cr, uid, [('period_id', '=', period_id)])
            bulletins = bulletin_obj.browse(cr, uid, bulletins)
            salaryline = {}
            columns = ['Matricule', 'Nom', 'Date', 'Fonction', u'Jours Travaillés',
                     'Salaire de base', 'HS', u'Indemnité',
                     u'Ancienneté', 'Evaluation', 'Gratification', 'Commissions', 'Brut', 'IRSA', 'CNaPS', 'FUNHECE', 'Net', u'Avance/Ret', 'Net a Payer', 'Virement', u'Espèce']
            columns_extra = []
            for bulletin in bulletins:
                salaryline[bulletin.employee_id.id] = []
                salaryline[bulletin.employee_id.id] = [{'Matricule':bulletin.employee_id.matricule}]
                salaryline[bulletin.employee_id.id][0].update({'Nom':bulletin.employee_id.name})
                salaryline[bulletin.employee_id.id][0].update({u'Jours Travaillés':bulletin.working_days})
                salaryline[bulletin.employee_id.id][0].update({'Brut':bulletin.salaire_brute})
                salaryline[bulletin.employee_id.id][0].update({'Net':bulletin.salaire_net})
                salaryline[bulletin.employee_id.id][0].update({'Net a Payer':bulletin.salaire_net_a_payer})
                salaryline[bulletin.employee_id.id][0].update({'Virement':bulletin.salaire_net_a_payer - bulletin.cash})
                salaryline[bulletin.employee_id.id][0].update({u'Espèce':bulletin.cash})
                salaryline[bulletin.employee_id.id][0].update({'Date':bulletin.employee_id.date})
                salaryline[bulletin.employee_id.id][0].update({'Fonction':bulletin.employee_id.job_id.name})
                salaryline[bulletin.employee_id.id][0].update({'HS':0})
                salaryline[bulletin.employee_id.id][0].update({'Commissions':0})
                salaryline[bulletin.employee_id.id][0].update({'Gratification':0})
                salaryline[bulletin.employee_id.id][0].update({'FUNHECE':0})
                salaryline[bulletin.employee_id.id][0].update({'CNaPS':0})
                salaryline[bulletin.employee_id.id][0].update({'IRSA':0})
                salaryline[bulletin.employee_id.id][0].update({u'Avance/Ret':0})
                salaryline[bulletin.employee_id.id][0].update({u'Ancienneté':0})
                salaryline[bulletin.employee_id.id][0].update({u'Indemnité':0})

                for line in bulletin.salary_line_ids:
                    if line.name[:1] == 'H':
                        salaryline[bulletin.employee_id.id][0]['HS'] += line.subtotal_employee
                    elif line.name[:4] == 'g320':
                        salaryline[bulletin.employee_id.id][0].update({u'Ancienneté':line.subtotal_employee})
                    elif line.name[:4] == 'g220':
                        salaryline[bulletin.employee_id.id][0].update({u'Indemnité':line.subtotal_employee})
                    elif line.name[:4] == 'g210':
                        salaryline[bulletin.employee_id.id][0].update({u'Indemnité':line.subtotal_employee})
                    elif line.name[:4] == 'r100':
                        salaryline[bulletin.employee_id.id][0].update({u'Avance/Ret':line.subtotal_employee
                                                                      + salaryline[bulletin.employee_id.id][0][u'Avance/Ret']})
                        salaryline[bulletin.employee_id.id][0].update({'Net':line.subtotal_employee
                                                                             + salaryline[bulletin.employee_id.id][0]['Net']})
                    elif line.name[:4] == 'g400':
                        salaryline[bulletin.employee_id.id][0].update({'Commissions':line.subtotal_employee + salaryline[bulletin.employee_id.id][0]['Commissions']})
                    elif line.name[:4] == 'CNaP':
                        salaryline[bulletin.employee_id.id][0].update({'CNaPS':line.subtotal_employee})
                    elif line.name[:4] == 'Impo':
                        salaryline[bulletin.employee_id.id][0].update({'IRSA':line.subtotal_employee})
                    elif line.name[:4] == 'Sala':
                        salaryline[bulletin.employee_id.id][0].update({'Salaire de base':line.subtotal_employee})
                    elif line.name[:4] in ['FUNH', 'SMIA']:
                        salaryline[bulletin.employee_id.id][0].update({'FUNHECE':line.subtotal_employee})
                    elif line.name[:4] == 'Grat':
                        line_eval = line.name[21:]
                        salaryline[bulletin.employee_id.id][0].update({'Evaluation':line_eval})
                        salaryline[bulletin.employee_id.id][0].update({'Gratification':line.subtotal_employee})
                    else:
                        if line.subtotal_employee != 0:
                            if line.name not in columns_extra:
                                columns_extra.append(line.name)
                            salaryline[bulletin.employee_id.id][0].update({unicode(line.name):line.subtotal_employee})

            record = {}
            sno = 0
            wbk = xlwt.Workbook()
            date_format = xlwt.XFStyle()
            num_format = xlwt.XFStyle()
            date_format.num_format_str = 'dd/mm/yyyy'
            num_format.num_format_str = '#,##0.00'
            style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;'
                                 'align: horiz center;''borders: left thin, right thin, top thin')
            style2 = xlwt.easyxf('font: bold on,color_index 0X36;'
                                 'align: horiz right;''borders: left thin, right thin, top thin', num_format_str='#,##0.00')
            s1 = 0
            sheet1 = wbk.add_sheet('Salaires')
            s2 = 1
            cols = 0
            for column in columns:
                sheet1.write(s1, cols, column, style1)
                sheet1.col(cols).width = len(column) * 367
                if column == 'Commissions':
                    for ec in columns_extra:
                        uec = unicode(ec)
                        cols += 1
                        sheet1.write(s1, cols, uec, style1)
                        sheet1.col(cols).width = len(uec) * 367
                cols += 1
            sheet1.row(0).height_mismatch = True
            sheet1.row(0).height = 325
            rows = 1
            for bulletin in bulletins:
                cols = 0
                sheet1.row(rows).height_mismatch = True
                sheet1.row(rows).height = 325
                for col in columns:
                    if col in salaryline[bulletin.employee_id.id][0]:
                        if col == 'Date':
                            date = datetime.strptime((salaryline[bulletin.employee_id.id][0][col]), '%Y-%m-%d')
                            sheet1.write(rows, cols, date, date_format)
                        elif col not in ['Nom', 'Matricule', 'Fonction', 'Evaluation']:
                            sheet1.write(rows, cols, salaryline[bulletin.employee_id.id][0][col], num_format)
                        else:
                            sheet1.write(rows, cols, salaryline[bulletin.employee_id.id][0][col])
                    else:
                        sheet1.write(rows, cols, 0)
                    if col == 'Commissions':
                        for ec in columns_extra:
                            cols += 1
                            if unicode(ec) in salaryline[bulletin.employee_id.id][0]:
                                if ec == "Arrondi":
                                    net = salaryline[bulletin.employee_id.id][0]['Net'] - salaryline[bulletin.employee_id.id][0][ec]
                                    salaryline[bulletin.employee_id.id][0].update({'Net':net})
                                sheet1.write(rows, cols, salaryline[bulletin.employee_id.id][0][unicode(ec)], num_format)
                            else:
                                sheet1.write(rows, cols, 0, num_format)
                    if col in salaryline[bulletin.employee_id.id][0]:
                        if type(salaryline[bulletin.employee_id.id][0][col]) == type(u'unicode'):
                            max = len(salaryline[bulletin.employee_id.id][0][col]) * 256
                        else:
                            max = len(str(salaryline[bulletin.employee_id.id][0][col])) * 256
                        if sheet1.col(cols).width < max:
                            sheet1.col(cols).width = max
                    cols += 1
                rows += 1
            alpha = string.ascii_uppercase
            for num in range(5, min(cols, 26)):
                # print alpha
                # print num
                end_sum = alpha[num]
                end_sum += str(rows)
                start_sum = alpha[num] + '1'
                sheet1.write(rows, num, xlwt.Formula('SUM(' + start_sum + ':' + end_sum + ')'), style2)
                sheet1.row(rows).height_mismatch = True
                sheet1.row(rows).height = 325
                max = len(str(salaryline[bulletin.employee_id.id][0][col])) * 256
                if sheet1.col(num).width < max:
                    sheet1.col(num).width = max
            file_data = StringIO.StringIO()
            wbk.save(file_data)
            out = base64.encodestring(file_data.getvalue())
            values = {
                        'name' : 'Journal_de_paie' + '.xls',
                        'datas' :  out,
                        'datas_fname' : 'Journal_de_paie' + '.xls',
                        'description' : 'Journal_de_paie ' + object.period_id.name,
                        'res_model' : 'hr.payroll_ma',
                        'partner_id':object.partner_id.id,
                        'res_id' : ids[0],
                    }
            attach_id.append(self.pool.get('ir.attachment').create(cr, uid, values, context=context))
        return attach_id

    def create_legal_reports(self, cr, uid, ids, context=None):
        cnaps = ['Periode', 'CNaPS_number', 'Nom', 'Matricule', u'Date Entrée', 'Date Sortie',
                     'Salaire Brut', 'Avantage', u'Temps Travaillés', u'Non-Plafoné', u'Plafoné', 'CNaPS Employeur', u'CNaPS Employé', 'Cin']
        funhece = ['Periode', 'CNaPS_number', 'Nom', 'Matricule', u'Date Entrée', 'Date Sortie',
                     'Salaire Brut', 'Avantage', u'Temps Travaillés', u'Non-Plafoné', u'Plafoné', 'FUNHECE Employeur', u'FUNHECE Employé', 'Cin']
        irsa = ['Periode', 'Matricule', 'Nom', 'Salaire Brut', 'Base Cotisations', 'CNaPS', 'FUNHECE', 'NET IMPOSABLE', 'IRSA']

        reports = {'irsa':irsa, 'cnaps':cnaps, 'medical':funhece}
        bulletin_obj = self.pool.get('hr.payroll_ma.bulletin')
        plafonds = {}
        created = []
        for object in self.browse(cr, uid, ids):
            bulletins = bulletin_obj.search(cr, uid, [('period_id', '=', object.period_id.id)])
            bulletins = bulletin_obj.browse(cr, uid, bulletins)
            cotisation_obj = self.pool.get('hr.payroll_ma.cotisation')
            cotisations = cotisation_obj.search(cr, uid, [])
            cotisations = cotisation_obj.browse(cr, uid, cotisations)
            plafonds = {}
            for cotisation in cotisations:
                plafonds.update({cotisation.name[0:4]:cotisation.plafond})

            salaryline = {}
            columns = ['Periode', 'CNaPS_number', 'Nom', 'Matricule', u'Date Entrée', 'Date Sortie',
                     'NET IMPOSABLE', 'Avantage', u'Temps Travaillés', u'Non-Plafoné', 'FUNHECE', 'Salaire Brut', 'IRSA', u'Temps Travaillés', ]

            for bulletin in bulletins:
                salaryline[bulletin.employee_id.id] = []
                salaryline[bulletin.employee_id.id] = [{'Matricule':bulletin.employee_id.matricule}]
                salaryline[bulletin.employee_id.id][0].update({'Nom':bulletin.employee_id.name})
                salaryline[bulletin.employee_id.id][0].update({u'Temps Travaillés':min(bulletin.working_days * 8, 173.33)})
                salaryline[bulletin.employee_id.id][0].update({'Salaire Brut':bulletin.salaire_brute})
                salaryline[bulletin.employee_id.id][0].update({u'Non-Plafoné':bulletin.salaire_brute})
                salaryline[bulletin.employee_id.id][0].update({'Net':bulletin.salaire_net})
                salaryline[bulletin.employee_id.id][0].update({'NET IMPOSABLE':bulletin.salaire_net_imposable})
                salaryline[bulletin.employee_id.id][0].update({'Virement':bulletin.salaire_net_a_payer - bulletin.cash})
                salaryline[bulletin.employee_id.id][0].update({u'Espèce':bulletin.cash})
                salaryline[bulletin.employee_id.id][0].update({u'Date Entrée':bulletin.employee_id.date})
                salaryline[bulletin.employee_id.id][0].update({'Fonction':bulletin.employee_id.job_id.name})
                salaryline[bulletin.employee_id.id][0].update({'FUNHECE':0})
                salaryline[bulletin.employee_id.id][0].update({'CNaPS':0})
                salaryline[bulletin.employee_id.id][0].update({'CNaPS_number':bulletin.employee_id.licenseno})
                salaryline[bulletin.employee_id.id][0].update({'IRSA':0})
                salaryline[bulletin.employee_id.id][0].update({'Periode':object.period_id.name})


                for line in bulletin.salary_line_ids:
                    if line.name[:4] in plafonds:
                        if 'plaf' + line.name[:4] not in columns:
                            columns.append('plaf' + line.name[:4])
                        salaryline[bulletin.employee_id.id][0].update({'plaf' + line.name[:4]:min(plafonds[line.name[:4]], bulletin.salaire_brute)})
                        salaryline[bulletin.employee_id.id][0].update({'Base Cotisations':min(plafonds[line.name[:4]], bulletin.salaire_brute)})
                        salaryline[bulletin.employee_id.id][0].update({u'Plafoné':min(plafonds[line.name[:4]], bulletin.salaire_brute)})

                    if line.name[:4] == 'CNaP':
                        salaryline[bulletin.employee_id.id][0].update({'CNaPS Employeur':line.subtotal_employer})
                        salaryline[bulletin.employee_id.id][0].update({u'CNaPS Employé':line.subtotal_employee})
                        salaryline[bulletin.employee_id.id][0].update({'CNaPS':line.subtotal_employee})
                        salaryline[bulletin.employee_id.id][0].update({'CNaPS Total':line.subtotal_employee + line.subtotal_employer})


                    elif line.name[:4] == 'Impo':
                        salaryline[bulletin.employee_id.id][0].update({'IRSA':line.subtotal_employee})
                    elif line.name[:4] == 'Sala':
                        salaryline[bulletin.employee_id.id][0].update({'Salaire de base':line.subtotal_employee})
                    elif line.name[:4] == 'FUNH':
                        salaryline[bulletin.employee_id.id][0].update({'FUNHECE Employeur':line.subtotal_employer})
                        salaryline[bulletin.employee_id.id][0].update({u'FUNHECE Employé':line.subtotal_employee})
                        salaryline[bulletin.employee_id.id][0].update({'FUNHECE':line.subtotal_employee})
                        salaryline[bulletin.employee_id.id][0].update({'FUNHECE Total':line.subtotal_employee + line.subtotal_employer})
                salaryline[bulletin.employee_id.id][0].update({'Cin':bulletin.employee_id.cin})

            for report in reports:
                record = {}
                sno = 0
                wbk = xlwt.Workbook()
                date_format = xlwt.XFStyle()
                num_format = xlwt.XFStyle()
                date_format.num_format_str = 'dd/mm/yyyy'
                num_format.num_format_str = '#,##0.00'
                style1 = xlwt.easyxf('font: bold on,height 240,color_index 0X36;'
                                     'align: horiz center;''borders: left thin, right thin, top thin')
                style2 = xlwt.easyxf('font: bold on,color_index 0X36;'
                                     'align: horiz right;''borders: left thin, right thin, top thin', num_format_str='#,##0.00')
                s1 = 0
                sheet1 = wbk.add_sheet(report)
                s2 = 1
                cols = 0
                for column in reports[report]:
                    sheet1.write(s1, cols, column, style1)
                    sheet1.col(cols).width = len(column) * 367
                    cols += 1
                sheet1.row(0).height_mismatch = True
                sheet1.row(0).height = 325
                rows = 1
                for bulletin in bulletins:
                    cols = 0
                    sheet1.row(rows).height_mismatch = True
                    sheet1.row(rows).height = 325
                    for col in reports[report]:
                        if col in salaryline[bulletin.employee_id.id][0]:
                            if col == 'Date':
                                date = datetime.datetime.strptime((salaryline[bulletin.employee_id.id][0][col]), '%Y-%m-%d')
                                sheet1.write(rows, cols, date, date_format)
                            elif col not in ['Periode', 'Nom', 'Matricule', 'Cin', 'CNaPS_number']:
                                amt = salaryline[bulletin.employee_id.id][0][col]
                                sheet1.write(rows, cols, amt, num_format)
                            else:
                                sheet1.write(rows, cols, salaryline[bulletin.employee_id.id][0][col])
                        else:
                            sheet1.write(rows, cols, 0)
                        if col in salaryline[bulletin.employee_id.id][0]:
                            if type(salaryline[bulletin.employee_id.id][0][col]) == type(u'unicode'):
                                max = len(salaryline[bulletin.employee_id.id][0][col]) * 256
                            else:
                                max = len(str(salaryline[bulletin.employee_id.id][0][col])) * 256
                            if sheet1.col(cols).width < max:
                                sheet1.col(cols).width = max
                        cols += 1
                    rows += 1
                alpha = string.ascii_uppercase
                for num in range(5, cols):
                    end_sum = alpha[num] + str(rows)
                    start_sum = alpha[num] + '1'
                    sheet1.write(rows, num, xlwt.Formula('SUM(' + start_sum + ':' + end_sum + ')'), style2)
                    sheet1.row(rows).height_mismatch = True
                    sheet1.row(rows).height = 325
                    max = len(str(salaryline[bulletin.employee_id.id][0][col])) * 256
                    if sheet1.col(num).width < max:
                        sheet1.col(num).width = max
                file_data = StringIO.StringIO()
                wbk.save(file_data)
                out = base64.encodestring(file_data.getvalue())
                values = {
                        'name' : report + '.xls',
                        'datas' :  out,
                        'datas_fname' : report + '.xls',
                        'description' : report + object.period_id.name,
                        'res_model' : 'hr.payroll_ma',
                        'partner_id':object.partner_id.id,
                        'res_id' : ids[0],
                    }
                attach_id = self.pool.get('ir.attachment').create(cr, uid, values, context=context)
                created.append(attach_id)
        return created

    def action_bank_file_create(self, cr, uid, ids, context=None):
        import base64
        payment_obj = self.pool.get('payment.term')
        payment_terms = payment_obj.search(cr, uid, [])  #
        payment_terms = payment_obj.browse(cr, uid, payment_terms)
        banks = []
        for pt in payment_terms:
            if pt.bank_id and pt.state == 'open':
                if pt.bank_id.name not in banks:
                    banks.append(pt.bank_id.name)
        # banks=['bgfi','bmoi','boa']
        created = []
        for bank in banks:
            name = 'Transfert_' + bank + '.txt'
            salary = self.browse(cr, uid, ids)[0]
            ###########################################
            if bank == 'BNI CREDIT LYONNAIS MADAGASCAR':
                transfer_count = 0
                transfer_amount = 0
                lines = ""
                for payslip in salary.bulletin_line_ids:
                    for ept in payslip.employee_id.payment_term_id:
                        if ept.bank_id.name == bank and ept.state == 'open':
                            if(ept.bank_account_number == False):
                                raise osv.except_osv(_('UserError'),
                                    _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                            else:
                                compte_bank = ept.bank_account_number
                                trf_amt = int(ept.amount and ept.amount or ept.rate / 100 * payslip.salaire_net_a_payer)  # ???
                                str_trf_amt = str(trf_amt)
                                c1 = compte_bank[0:5]  # code bank
                                c2 = compte_bank[5:10]  # code guichet ou agence
                                c3 = compte_bank[10:21]  # numero de compte
                                c4 = compte_bank[21:23]  # rib
                                c5 = str(payslip.employee_id.name)  # nom
                                c6[15 - len(str_trf_amt):15] = str_trf_amt  # montant
                                c7 = str(payslip.employee_id.bank)  # observation
                                description = 'SALAIRE ' + salary.period_id.name
                                c8[0:len(description)] = description
                                transfer_count += 1
                                transfer_amount += trf_amt
                                line = ''.join(compte_bank), ''.join(c6), ''.join(payslip.employee_id.matricule), ''.join(c5), '\r\n'
                                line = ''.join(line)
                                lines += line
                # h1='0302                     '
                h1 = 'CODE BANQUE'
                # h2=datetime.strftime(datetime.strptime(salary.date_transfer,'%Y-%m-%d'),'%d%m%Y')[0:4]
                h2 = 'CODE GUICHET'
                # h3=datetime.strftime(datetime.strptime(salary.date_transfer,'%Y-%m-%d'),'%y')[1]
                h3 = 'N COMPTE'
                # h4[0:len(salary.partner_id.name[:24])]=salary.partner_id.name[:24]
                h4 = 'CLE RIB'
                # h5='                          F     '
                h5 = 'NOM'

                h6 = 'MONTANT'
                h7 = 'OBSERVATIONS BANQUE/DOMICILIATION'
                # header=''.join(h1),''.join(h2),''.join(h3),''.join(h4),''.join(h5),''.join(h6),''.join(h7),'\r\n'
                # content=''.join(header)
                content += lines
                footer = '0802', ''.join(h10), ''.join(h15)
                footer = ''.join(footer)
                content += footer
            ###########################################
            elif bank == 'B.F.V. SOCIETE GENERALE':
                transfer_count = 0
                transfer_amount = 0
                lines = ""
                c7 = datetime.strftime(datetime.strptime(salary.date_transfer, '%Y-%m-%d'), '%d/%m/%Y')  # date de transfert
                c8 = str(salary.period_id.name)  # periode (08/2014)
                c8 = c8.split("/")
                c8 = c8[0] + '/' + c8[1][2:4]
                for payslip in salary.bulletin_line_ids:
                    for ept in payslip.employee_id.payment_term_id:
                        if ept.bank_id.name == bank and ept.state == 'open':
                            if(ept.bank_account_number == False):
                                raise osv.except_osv(_('UserError'),
                                    _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                            else:
                                matricule_emp = str(payslip.employee_id.matricule)
                                compte_bank = ept.bank_account_number
                                trf_amt = round(float(ept.amount and ept.amount or ept.rate / 100 * payslip.salaire_net_a_payer), 2)  # ???
                                str_trf_amt = str(trf_amt)
                                amnt = str_trf_amt.split(".")
                                amntB = amnt[0]
                                amntc = amnt[1]
                                amntc = str(amntc)
                                c = ''
                                if len(amntc) < 2:
                                    comp = 2 - len(amntc)
                                    comp = ['0' * comp]
                                    c = amntc + ''.join(comp)
                                else:
                                    c = amntc[0:2]
                                str_trf_amt = str(amntB) + ',' + c

                                c1 = compte_bank[0:5]  # code bank
                                c2 = "0000000132"
                                Lg = int(len(compte_bank) - 5)
                                c3 = compte_bank[5:Lg]  # code restant
                                c4 = str(payslip.employee_id.name)  # nom en 39 caractere maximun
                                Lc4 = len(c4)
                                if Lc4 < 40:
                                    complement_char = 40 - Lc4
                                    espace = [' ' * complement_char]
                                    c4 = c4 + ''.join(espace)  # nom en format 40 caractere
                                elif Lc4 >= 40:
                                    c4 = c4[0:39] + ' '
                                # c7=datetime.strftime(datetime.strptime(salary.date_transfer,'%Y-%m-%d'),'%d%m%Y')[0:4]
                                Lg_amount = len(str_trf_amt)
                                c5 = ''  # montant
                                if Lg_amount < 12:
                                    v = 12 - int(Lg_amount)
                                    zero = ['0' * v]
                                    amount_str = ''.join(zero) + str_trf_amt
                                    c5 = str(amount_str)
                                c6 = ''
                                if len(matricule_emp) < 6:
                                    complement_zero = 6 - len(matricule_emp)
                                    mat = ['0' * complement_zero]
                                    c6 = ''.join(mat) + matricule_emp
                                else:
                                    c6 = str(matricule_emp)
                                c7 = str(c7)
                                transfer_count += 1
                                transfer_amount += trf_amt
                                line = '\n', ''.join(c1), ''.join(c2), ''.join(c3), ''.join(c4), ''.join(c7), ''.join(c5), ''.join(c6), ''.join(c8),  # '---',str(Lg_amount)
                                line = ''.join(line)
                                lines += line
                content = ''
                content += lines
            ###########################################
            elif bank == 'B.O.A. MADAGASCAR':
                transfer_count = 0
                transfer_amount = 0
                lines = ""
                for payslip in salary.bulletin_line_ids:
                    for ept in payslip.employee_id.payment_term_id:
                        if ept.bank_id.name == bank and ept.state == 'open':
                            if(ept.bank_account_number == False):
                                raise osv.except_osv(_('UserError'),
                                    _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                            else:
                                compte_bank = ept.bank_account_number
                                trf_amt = int(ept.amount and ept.amount or ept.rate / 100 * payslip.salaire_net_a_payer)  # ???
                                str_trf_amt = str(trf_amt)
                                c1 = compte_bank[0:5]  # code bank
                                c2 = compte_bank[5:10]  # code guichet ou agence
                                c3 = compte_bank[10:21]  # numero de compte
                                c4 = compte_bank[21:23]  # rib
                                c5 = str(payslip.employee_id.name)  # nom
                                lg = 15 - len(str_trf_amt)
                                if lg != 0:
                                    complement_char = [' ' * lg]

                                # c6[0:15]=''.join(complement_char)str_trf_amt #montant
                                c6 = str_trf_amt  # montant
                                c7 = str(payslip.employee_id.bank)  # observation
                                description = 'SALAIRE ', str(salary.period_id.name)
                                # c8[0:len(description)]=description
                                c8 = description
                                transfer_count += 1
                                transfer_amount += trf_amt
                                line = ''.join(c1), ''.join(c2), ''.join(c3), ''.join(c4), ''.join(c5), ''.join(c6), ''.join(c7), ''.join(c8), '\r\n'
                                line = ''.join(line)
                                lines += line
                # h1='0302                     '
                h1 = 'CODE BANQUE'
                # h2=datetime.strftime(datetime.strptime(salary.date_transfer,'%Y-%m-%d'),'%d%m%Y')[0:4]
                h2 = 'CODE GUICHET'
                # h3=datetime.strftime(datetime.strptime(salary.date_transfer,'%Y-%m-%d'),'%y')[1]
                h3 = 'N COMPTE'
                # h4[0:len(salary.partner_id.name[:24])]=salary.partner_id.name[:24]
                h4 = 'CLE RIB'
                # h5='                          F     '
                h5 = 'NOM'

                h6 = 'MONTANT'
                h7 = 'OBSERVATIONS BANQUE/DOMICILIATION'
                header = ''.join(h1), ''.join(h2), ''.join(h3), ''.join(h4), ''.join(h5), ''.join(h6), ''.join(h7), '\r\n'
                content = ''.join(header)
                content += lines
                footer = '0802                                                                                                  ', ''.join(h10), ''.join(h15)
                footer = ''.join(footer)
                content += footer
            ###########################################
            elif bank == 'B.G.F.I.':
                h1 = list(" "*1)
                h2 = list(" "*8)
                h3 = list(" "*6)
                h4 = list(" "*36)
                h5 = list(" "*28)
                h9 = list(" "*6)
                h10 = list("0"*20)
                h11 = list(" "*30)
                h12 = list(" "*120)

                transfer_count = 0
                transfer_amount = 0
                lines = ""
                for payslip in salary.bulletin_line_ids:
                    for ept in payslip.employee_id.payment_term_id:
                        if ept.bank_id.name == bank and ept.state == 'open':
                            if(ept.bank_account_number == False):
                                raise osv.except_osv(_('UserError'),
                                    _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                            else:
                                compte_bank = ept.bank_account_number
                                trf_amt = int(ept.amount and ept.amount or ept.rate / 100 * payslip.salaire_net_a_payer)  # ???
                                str_trf_amt = str(trf_amt)
                                c1 = list('2')
                                c2 = list(' ' * 12)
                                c3 = list(' ' * 36)
                                c3[0:len(payslip.employee_id.name[:36])] = payslip.employee_id.name[:36]
                                c4 = list(' ' * 24)
                                c5 = list(' ' * 26)
                                c6 = list(' ' * 2)
                                if(payslip.employee_id.compte == False):
                                    raise osv.except_osv(_('UserError'),
                                        _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                                compte = payslip.employee_id.compte.replace(' ', '')
                                rib = compte[len(compte) - 2:]
                                compte = compte[0:len(compte) - 2]
                                c5[0:len(compte[:26])] = compte[:26]
                                c6 = list('0' * 20)
                                # str_trf_amt=str(int((payslip.salaire_net_a_payer-payslip.cash)*100))
                                c6[20 - len(str_trf_amt):20] = str_trf_amt
                                c7 = list(' ' * 30)
                                description = 'SALAIRE' + salary.period_id.name
                                c7[0:len(description)] = description
                                transfer_count += 1
                                transfer_amount += trf_amt
                                line = ''.join(c1), ''.join(c2), ''.join(c3), ''.join(c4), ''.join(c5), rib, ''.join(c6), ''.join(c7), '\r\n'
                                line = ''.join(line)
                                lines += line
                h1 = '1'

                h2[0:8] = datetime.strftime(datetime.strptime(salary.date_transfer, '%Y-%m-%d'), '%d%m%Y')
                h3[0:6] = datetime.strftime(datetime.strptime(salary.date_transfer, '%Y-%m-%d'), '%d%m%y')
                h4[0:len(salary.partner_id.name[:36])] = salary.partner_id.name[:36]
                compte = salary.bank_id.acc_number.replace(' ', '')
                rib = compte[len(compte) - 2:]
                compte = compte[0:len(compte) - 2]
                h5[0:len(compte[:28])] = compte[:28]
                h9[0:len(str(transfer_count))] = str(transfer_count)
                str_trf_amt = str(int(transfer_amount * 100))
                h10[20 - len(str_trf_amt):20] = str_trf_amt
                description = 'SALAIRE' + salary.period_id.name
                h11[0:len(description)] = description
                header = ''.join(h1), ''.join(h2), ''.join(h3), ''.join(h4), ''.join(h5), rib, ''.join(h9), ''.join(h10), ''.join(h11), '\r\n'
                content = ''.join(header)
                content += lines
            elif bank == 'B.M.O.I.':
                h1 = list(" "*18)
                h2 = list(" "*4)
                h3 = list(" "*1)
                h4 = list(" "*24)
                h5 = list(" "*26)
                h9 = list(" "*6)
                h6 = list(" "*16)
                h10 = list("0"*16)
                h11 = list(" "*16)
                h12 = list(" "*1)
                h13 = list(" "*31)
                h14 = list(" "*5)

                transfer_count = 0
                transfer_amount = 0
                lines = ""
                for payslip in salary.bulletin_line_ids:
                    for ept in payslip.employee_id.payment_term_id:
                        if ept.bank_id.name == bank and ept.state == 'open':
                            if(ept.bank_account_number == False):
                                raise osv.except_osv(_('UserError'),
                                    _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                            else:
                                compte_bank = ept.bank_account_number
                                trf_amt = int(ept.amount and ept.amount or ept.rate / 100 * payslip.salaire_net_a_payer)  # ???
                                str_trf_amt = str(trf_amt)
                                c1 = list('0602              ')
                                c2 = list(str(payslip.employee_id.matricule) + '       ')
                                c3 = list(' ' * 23)
                                c3[0:len(payslip.employee_id.name[:23])] = payslip.employee_id.name[:23]
                                c4 = list(' ' * 1)
                                c5 = list(' ' * 32)
                                c5[0:len(payslip.employee_id.bank[:32])] = payslip.employee_id.bank[:32]
                                c6 = list('0' * 16)
                                if(payslip.employee_id.compte == False):
                                    raise osv.except_osv(_('UserError'),
                                        _('Compte de banque incoherent %s:%s') % (payslip.employee_id.matricule, payslip.employee_id.name))
                                compte = payslip.employee_id.compte.replace(' ', '')
                                rib = compte[0:5]
                                compte = compte[6:len(compte) - 2]
                                c6[1:len(compte[:16])] = compte[:16]
                                c7 = list('0' * 15)
                                # str_trf_amt=str(int((payslip.salaire_net_a_payer-payslip.cash)*100))
                                c7[15 - len(str_trf_amt):15] = str_trf_amt
                                c8 = list(' ')
                                c9 = list(' ' * 30)
                                c11 = list(' ' * 6)
                                description = 'SALAIRE ' + salary.period_id.name
                                c9[0:len(description)] = description
                                c10 = list(rib)
                                transfer_count += 1
                                transfer_amount += trf_amt
                                line = ''.join(c1), ''.join(c2), ''.join(c3), ''.join(c4), ''.join(c5), ''.join(c6), ''.join(c7), ''.join(c8), ''.join(c9), ''.join(c10), ''.join(c11), '\r\n'
                                line = ''.join(line)
                                lines += line
                h1 = '0302                     '
                h2 = datetime.strftime(datetime.strptime(salary.date_transfer, '%Y-%m-%d'), '%d%m%Y')[0:4]
                h3 = datetime.strftime(datetime.strptime(salary.date_transfer, '%Y-%m-%d'), '%y')[1]
                h4[0:len(salary.partner_id.name[:24])] = salary.partner_id.name[:24]
                h5 = '                          F     '
                compte = salary.bank_id.acc_number.replace(' ', '')
                rib = compte[len(compte) - 2:]
                head = compte[0:5]
                compte = compte[0:len(compte) - 2]
                h6[0:len(compte[:16])] = compte[:16]
                h9[0:len(str(transfer_count))] = str(transfer_count)
                str_trf_amt = str(int(transfer_amount * 100))
                h10[16 - len(str_trf_amt):16] = str_trf_amt
                description = 'SALAIRE' + salary.period_id.name
                h11[0:len(description)] = description
                h12 = list(' ' * 47)
                h15 = list(' ' * 42)
                h13 = list(' ' * 6)
                h14[0:5] = head
                header = ''.join(h1), ''.join(h2), ''.join(h3), ''.join(h4), ''.join(h5), ''.join(h6), ''.join(h12), ''.join(h14), ''.join(h13), '\r\n'
                content = ''.join(header)
                content += lines
                footer = '0802                                                                                                  ', ''.join(h10), ''.join(h15)
                footer = ''.join(footer)
                content += footer
            values = {
                        'name' : name,
                        'datas' :  base64.encodestring(content.encode('utf-8')),
                        'datas_fname' : name,
                        'description' : 'fichier de Banque',
                        'res_model' : 'hr.payroll_ma',
                        'partner_id':1,
                        'res_id' : ids[0],
                    }
            attach_id = self.pool.get('ir.attachment').create(cr, uid, values, context=context)
            created.append(attach_id)
        return created
        # return {
        #     'type': 'ir.actions.act_window',
        #     'name': name,
        #     'view_type': 'form',
        #     'view_mode': 'tree,form',
        #     'context': context,
        #     'domain' : [('id','in',created)],
        #     'res_model': 'ir.attachment',
        #     'nodestroy': True,
        # }

    def compute_hs(self, cr, uid, ids, context={}):
        """
            hr_payroll_ma
        """
        overtime_obj = self.pool.get('hr.employee.overtime')
        bulletin_obj = self.pool.get('hr.payroll_ma.bulletin')
        for payroll in self.browse(cr, uid, ids):
            period_id = payroll.period_id.id
            overtimes = overtime_obj.search(cr, uid, [('period_id', '=', period_id), ('state', '=', 'valid'), ('type', '=', 'hs')])
            holidays = overtime_obj.search(cr, uid, [('period_id', '=', period_id), ('state', '=', 'valid'), ('type', '=', 'ferie')])
            nights = overtime_obj.search(cr, uid, [('period_id', '=', period_id), ('state', '=', 'valid'), ('type', '=', 'nuit')])
            extranights = overtime_obj.search(cr, uid, [('period_id', '=', period_id), ('state', '=', 'valid'), ('type', '=', 'nuit_extra')])

            holidays = overtime_obj.browse(cr, uid, holidays)
            nights = overtime_obj.browse(cr, uid, nights)
            overtimes = overtime_obj.browse(cr, uid, overtimes)
            extranights = overtime_obj.browse(cr, uid, extranights)
            sunday = 0
            overtime_table = {}
            holiday_table = {}
            night_table = {}
            extranight_table = {}

            for night in nights:
               if night.name.id not in night_table:
                   night_table[night.name.id] = night.hours
               else:
                   night_table[night.name.id] += night.hours
            for holiday in holidays:
               if holiday.name.id not in holiday_table:
                   holiday_table[holiday.name.id] = holiday.hours
               else:
                   holiday_table[holiday.name.id] += holiday.hours
            for extranight in extranights:
               if extranight.name.id not in extranight_table:
                   extranight_table[extranight.name.id] = extranight.hours
               else:
                   extranight_table[extranight.name.id] += extranight.hours

            for overtime in overtimes:
                if not overtime.date_start:
                    dt = payroll.date_salary
                else:
                    dt = overtime.date_start
                day = datetime.strptime(dt[:10], '%Y-%m-%d').weekday()
                if overtime.name.id not in overtime_table:
                    overtime_table[overtime.name.id] = {}
                if 'sunday' not in overtime_table[overtime.name.id]:
                    overtime_table[overtime.name.id]['sunday'] = 0
                if day == 6:
                    overtime_table[overtime.name.id]['sunday'] += overtime.hours
                else:
                    if overtime.week not in overtime_table[overtime.name.id]:
                        overtime_table[overtime.name.id][overtime.week] = overtime.hours
                    else:
                        overtime_table[overtime.name.id][overtime.week] += overtime.hours



            weekly = {}
            for employee in overtime_table:
                # raise osv.except_osv(_('employee'),_('employee = %s')%(employee)) #1179
                ot1 = 0
                ot2 = 0
                weekly_ot_limit = 8
                # ARO
                weekly_ot_limit = 0
                # /ARO
                for week in overtime_table[employee]:
                    # raise osv.except_osv(_('week'),_('week = %s')%(week))
                    ot1 += overtime_table[employee][week]
                if employee in holiday_table:
                    ferie = holiday_table[employee]
                else:
                    ferie = 0
                if employee in night_table:
                    night = night_table[employee]
                else:
                    night = 0
                if employee in extranight_table:
                    extranight = extranight_table[employee]
                else:
                    extranight = 0
                # ARO Custom - no weekly overtime
                ot1 *= 60
		ot2 *= 60
		sunday *= 60
		ferie *= 60
                nuit = night
		nuit *= 60
                nuit_extra = extranight
		nuit_extra *= 60
                total_overtime = ot1 + ot2
                if ot1 > 4800:
                    ot2 = ot1 - 4800
                    ot1 = 4800
                else:
                    ot1 = total_overtime
                    ot2 = 0
                # End Aro Custom
                if employee not in weekly:
                    weekly[employee] = {'ot1':ot1 / 60, 'ot2':ot2 / 60, 'sunday':overtime_table[employee]['sunday'] / 60, 'ferie':ferie / 60, 'night':night / 60, 'nuit_extra':extranight / 60}
                else:
                    weekly[employee]['ot1'] += ot1 / 60
                    weekly[employee]['ot2'] += ot2 / 60

                # raise osv.except_osv(_('hs'),_('hs = %s')%(weekly))

            for bulletin in payroll.bulletin_line_ids:
                if bulletin.employee_id.id in weekly:
                    ot1 = weekly[bulletin.employee_id.id]['ot1']
                    ot2 = weekly[bulletin.employee_id.id]['ot2']
                    sunday = weekly[bulletin.employee_id.id]['sunday']
                    ferie = weekly[bulletin.employee_id.id]['ferie']
                    nuit = weekly[bulletin.employee_id.id]['night']
                    nuit_extra = weekly[bulletin.employee_id.id]['nuit_extra']
                    bulletin_obj.write(cr, uid, [bulletin.id], {'normal':ot1, 'overtime_hours':ot2, 'sundays':sunday, 'ferie':ferie, 'nuit':nuit, 'nuit_extra':nuit_extra})
        return True

    def generate_employees(self, cr, uid, ids, context={}):
        """
            method permettant de creer un bulletin
            pour tous les employes
        """
        employees = self.pool.get('hr.employee')
        obj_contract = self.pool.get('hr.contract')
        ids_employees = employees.search(cr, uid, [('active', '=', True)])
        emp = employees.read(cr, uid, ids_employees, ['id', 'name'])
        payroll_ma = self.pool.get('hr.payroll_ma').browse(cr, uid, ids[0])

        line = {}
        period_date_start = payroll_ma.period_id.date_start
        period_date_end = payroll_ma.period_id.date_stop  # date_start auparavant

        if payroll_ma.state == 'draft':
            sql = '''
            DELETE from hr_payroll_ma_bulletin where id_payroll_ma = %s
                '''
            cr.execute(sql, (ids[0],))
        bulletin_name = 0
        for e in emp :
            result = self.pool.get('hr.payroll_ma.bulletin').onchange_employee_id(cr, uid, ids, e['id'], payroll_ma.period_id.id)['value']
            employee = self.pool.get('hr.employee').browse(cr, uid, e['id'])
            contract_ids = obj_contract.search(cr, uid, [('employee_id', '=', e['id'])
                            , ('date_start', '<=', payroll_ma.period_id.date_stop)]
                            , order='date_start desc', context=context)
            bulletin_name += 1
            if contract_ids:
                name = str(bulletin_name).zfill(4) + '-' + payroll_ma.period_id.name
                con = contract_ids[-1:][0]
                con = contract_ids[0]
                contract = obj_contract.browse(cr, uid, con)
                line = {
                'employee_id' : e['id'], 'employee_contract_id' : con, 'working_days':result['working_days'],
                'normal_hours' : result['normal_hours'], 'hour_base' : result['hour_base'],
                'salaire_base' : contract.wage, 'id_payroll_ma':ids[0], 'period_id':payroll_ma.period_id.id,
                'name':name
                }
                result = self.pool.get('hr.payroll_ma.bulletin').create(cr, uid, line)
                print result
        return True

    def compute_all_lines(self, cr, uid, ids, context={}):
        for sal in self.browse(cr, uid, ids):
            bulletins = self.pool.get('hr.payroll_ma.bulletin').search(cr, uid, [('id_payroll_ma', '=', sal.id)])
            bulletins2 = self.pool.get('hr.payroll_ma.bulletin').browse(cr, uid, bulletins)
            for bul in bulletins2:
                bul.compute_all_lines()
        return True

    def run_payroll(self, cr, uid, ids, context=None):
        self.generate_employees(cr, uid, ids)
        self.compute_hs(cr, uid, ids)
        self.compute_all_lines(cr, uid, ids)
    # #generation des ecriture comptable

    def print_payslips(self, cr, uid, ids, context=None):
        datas = {'ids': self.pool.get('hr.payroll_ma.bulletin').search(cr, uid, [('id_payroll_ma', 'in', ids)])}
        return {
            'type': 'ir.actions.report.xml',
            'nodestroy':True,
            'report_name': 'hr.payroll_ma.bulletin.2',
            'datas': datas,
       }

    def action_move_create(self, cr, uid, ids):
        context = {}
        # pool = pooler.get_pool(cr.dbname)
        params = self.pool.get('hr.payroll_ma.parametres')
        ids_params = params.search(cr, uid, [])
        dictionnaire = params.read(cr, uid, ids_params[0])
        for sal in self.browse(cr, uid, ids):
            company_currency = sal.currency_id.id

            # one move line per salary period

            date = sal.date_salary or time.strftime('%Y-%m-%d')
            partner = sal.partner_id.id

            journal_id = sal.journal_id.id
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('Cannot create salary move on centralised journal'))

            period_id = sal.period_id and sal.period_id.id or False
            if not period_id:
                raise osv.except_osv(_('UserError'),
                        _('Periode obligatoire'))

            move = {}
            move_lines = []
            bulletins = self.pool.get('hr.payroll_ma.bulletin').search(cr, uid, [('id_payroll_ma', '=', sal.id)])
            bulletins_query_cond = str(tuple(bulletins))
            if tuple(bulletins).__len__() == 1:
                # string = str(tuple(bulletins)).remove(',')
                bulletins_query_cond = '(' + str(bulletins[0]) + ')'


            sql = """
                SELECT l.name as name , sum(subtotal_employee) as subtotal_employee,sum(subtotal_employer) as subtotal_employer,l.credit_account_id,l.debit_account_id
                FROM hr_payroll_ma_bulletin_line l
                LEFT JOIN account_account aa ON aa.id=l.credit_account_id
                RIGHT JOIN account_account ab ON ab.id=l.debit_account_id
                where l.type = 'cotisation' and id_bulletin in %s
                group by l.name,l.credit_account_id,l.debit_account_id
                """ % (bulletins_query_cond)
            cr.execute(sql)
            data = cr.dictfetchall()
            # def action_move_create2(self, cr, uid, ids):
            for line in data :
                if line['subtotal_employee'] :
                        #=======================================================
                        # move_line_debit={
                        #             'account_id' : sal.employee_contract_id.salary_debit_account_id.id,
                        #             'period_id' : period_id,
                        #             'journal_id' : journal_id,
                        #             'date' : date,
                        #             'name' : (line.name or '\\' )+ ' Salarial',
                        #             'debit' : line.subtotal_employee,
                        #             'partner_id' : line.partner_id and line.partner_id.id,
                        #             'currency_id': company_currency,
                        #             }
                        #=======================================================
                    move_line_credit = {
                                     'account_id' : line['credit_account_id'],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : (line['name'] or '\\') + ' Salarial',
                                     'credit' : line['subtotal_employee'],
                                     'debit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
                        # move_lines.append((0,0,move_line_debit))
                    move_lines.append((0, 0, move_line_credit))

                if line['subtotal_employer'] :
                        move_line_debit = {
                                     'account_id' : line['debit_account_id'],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : (line['name'] or '\\') + ' Patronal',
                                     'debit' : line['subtotal_employer'],
                                     'credit' :0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
                        move_line_credit = {
                                     'account_id' : line['credit_account_id'],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : (line['name'] or '\\') + ' Patronal',
                                     'debit' : 0,
                                     'credit' : line['subtotal_employer'],
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
                        move_lines.append((0, 0, move_line_debit))
                        move_lines.append((0, 0, move_line_credit))

            sql = '''
                SELECT sum(subtotal_employee) as sum,l.name as name,l.credit_account_id as credit_account_id,l.debit_account_id as debit_account_id
                FROM hr_payroll_ma_bulletin_line l
                LEFT JOIN account_account aa ON aa.id=l.credit_account_id
                RIGHT JOIN account_account ab ON ab.id=l.debit_account_id
                where l.type in ('majoration','retenu') and id_bulletin in %s
                group by l.name,l.credit_account_id,l.debit_account_id
                ''' % (bulletins_query_cond)
            cr.execute(sql)
            datas = cr.dictfetchall()

            for data in datas:
                move_line_debit_deduction = {
                                     'account_id' : data['debit_account_id'],
                                     'analytic_account_id': dictionnaire['analytic_account_id'][0],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : data['name'],
                                     'debit' :  data['sum'],
                                     'credit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }

                move_line_credit_deduction = {
                                     'account_id' : data['credit_account_id'],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : data['name'],
                                     'credit' : data['sum'],
                                     'debit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
                move_lines.append((0, 0, move_line_debit_deduction))
                move_lines.append((0, 0, move_line_credit_deduction))
            sql = '''
                SELECT sum(salaire_brute) as salaire_brute,sum(salaire_net_a_payer) as salaire_net_a_payer,sum(arrondi) as arrondi,sum(deduction) as deduction
                FROM hr_payroll_ma_bulletin b
                LEFT JOIN hr_payroll_ma pm ON pm.id=b.id_payroll_ma
                where b.id_payroll_ma = %s
                ''' % (sal.id)
            cr.execute(sql)
            data = cr.dictfetchall()

            data = data[0]
            move_line_debit = {
                                     'account_id' : dictionnaire['salary_debit_account_id'][0],
                                     'analytic_account_id': dictionnaire['analytic_account_id'][0],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : 'Salaire Brute',
                                     'debit' :  data['salaire_brute'],  # -data['deduction'],
                                     'credit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
            move_line_arrondi = {
                                     'account_id' : dictionnaire['roundoff_account_id'][0],
                                     'analytic_account_id': dictionnaire['analytic_account_id'][0],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : 'Arrondi',
                                     'debit' :  data['arrondi'],
                                     'credit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
            move_line_credit = {
                                     'account_id' : dictionnaire['salary_credit_account_id'][0],
                                     'period_id' : period_id,
                                     'journal_id' : journal_id,
                                     'date' : date,
                                     'name' : 'Salaire net a payer',
                                     'credit' : data['salaire_net_a_payer'],
                                     'debit' : 0,
                                     'partner_id' : partner,
                                     # 'currency_id': company_currency,
                                     'state' : 'valid'
                                     }
            move_lines.append((0, 0, move_line_debit))
            move_lines.append((0, 0, move_line_arrondi))
            move_lines.append((0, 0, move_line_credit))


            move = {'ref': sal.number,
                  'period_id' : period_id,
                  'journal_id' : journal_id,
                  'date' : date,
                  'state' : 'draft',
                  'name' : sal.name or '\\',
                  'line_id' : move_lines}
            move_id = self.pool.get('account.move').create(cr, uid, move)
            self.pool.get('hr.payroll_ma').write(cr, uid, sal.id, {'move_id' : move_id})
            return True

hr_payroll_ma()

class hr_payroll_ma_bulletin(osv.osv):


    _name = "hr.payroll_ma.bulletin"
    _description = 'bulletin'
    _order = "name,period_id desc"


    # ajout de nouvelle fonction

    def _get_previous_salary(self, cr, uid, ids, fields, arg, context=None):
        """
            retourne la valeur du salaire Precedent
        """
        res = {}
        obj_period = self.pool.get('account.period')
        for sal in self.browse(cr, uid, ids, context=context):
            code = str(sal.period_id.code).split('/')
            annee = int(code[1])
            code_int = int(code[0])
            if code_int < 10 and code_int > 1:
                code_int = code_int - 1
            elif code_int == 1:
                code_int = 12
                annee = annee - 1
            else:
                code_int = code_int - 1

            annee = str(annee)
            code_str = str(code_int)
            if len(code_str) < 2:
                code = '0' + code_str + '/' + annee
            else:
                code = code_str + '/' + annee

            period_id = obj_period.search(cr, uid, [('code', '=', code)])[0]
            sal_ids = self.search(cr, uid, [('employee_id', '=', sal.employee_id.id), ('period_id', '=', period_id)])
            if sal_ids and len(sal_ids) != 0:
                montant = self.read(cr, uid, sal_ids, ['salaire_net'])[0]
                res[sal.id] = montant['salaire_net']
            else:
                res[sal.id] = 0.0
        return res

    def _get_salary_difference(self, cr, uid, ids, fields, arg, context=None):
        """
            retourne la difference entre le salaire
            Precedent et le salaire actuelle
        """
        res = {}
        obj_period = self.pool.get('account.period')
        for sal in self.browse(cr, uid, ids, context=context):
            # raise osv.except_osv(_('salaire actuel'),_('salaire_net = %s')%(sal.salaire_net))
            code = str(sal.period_id.code).split('/')
            annee = int(code[1])
            code_int = int(code[0])
            if code_int < 10 and code_int > 1:
                code_int = code_int - 1
            elif code_int == 1:
                code_int = 12
                annee = annee - 1
            else:
                code_int = code_int - 1

            annee = str(annee)
            code_str = str(code_int)
            if len(code_str) < 2:
                code = '0' + code_str + '/' + annee
            else:
                code = code_str + '/' + annee

            period_id = obj_period.search(cr, uid, [('code', '=', code)])[0]
            sal_ids = self.search(cr, uid, [('employee_id', '=', sal.employee_id.id), ('period_id', '=', period_id)])
            if sal_ids and len(sal_ids) != 0:
                montant = self.read(cr, uid, sal_ids, ['salaire_net'])[0]
                res[sal.id] = sal.salaire_net - montant['salaire_net']
            else:
                res[sal.id] = sal.salaire_net - 0.0
        return res

    # fin

    _columns = {
        'name': fields.char('Numero du salaire', size=32, readonly=True),
        'date_salary': fields.date('Date salaire', select=1),
        'employee_id': fields.many2one('hr.employee', 'Employe', change_default=True, readonly=True, required=True, select=1),
        'matricule':fields.related('employee_id', 'matricule', type='char', string='Matricule'),
        'period_id': fields.many2one('account.period', 'Periode', select=1),
        'salary_line_ids': fields.one2many('hr.payroll_ma.bulletin.line', 'id_bulletin', 'lignes de salaire', readonly=True,),
        'employee_contract_id' : fields.many2one('hr.contract', 'Contrat de travail', required=True),
        'id_payroll_ma': fields.many2one('hr.payroll_ma', 'Ref Salaire', ondelete='cascade', select=True),
        'salaire_base' : fields.float('Salaire de base'),
        'normal_hours' : fields.float('Heures travaillee durant le mois'),
        'overtime_hours' : fields.float('Heures supplementaires'),
        'absences' : fields.float('Absences Horaires'),
        'cash' : fields.float('Espece'),
        'sundays' : fields.float('Dimanches'),
        'normal' : fields.float('HS Normale'),
        'extra' : fields.float('HS Extra'),
        'ferie' : fields.float('HS Ferie'),
        'nuit' : fields.float('Nuit'),
        'nuit_extra' : fields.float('Nuit Extra'),
        'hour_base' : fields.float('Salaire heure'),
        'comment': fields.text('Informations complementaires'),
        'salaire':fields.float('Salaire Base', readonly=True, digits=(16, 2)),
        'salaire_brute':fields.float('Salaire Brute', readonly=True, digits=(16, 2)),
        'salaire_brute_imposable':fields.float('Salaire brute imposable', readonly=True, digits=(16, 2)),
        'salaire_net':fields.float('Salaire Net', readonly=True, digits=(16, 2)),
        'salaire_net_a_payer':fields.float('Salaire Net a payer', readonly=True, digits=(16, 2)),
        'salaire_net_imposable':fields.float('Salaire Net Imposable', readonly=True, digits=(16, 2)),
        'cotisations_employee':fields.float('Cotisations Employe', readonly=True, digits=(16, 2)),
        'cotisations_employer':fields.float('Cotisations Employeur', readonly=True, digits=(16, 2)),
        'igr':fields.float('Impot sur le revenu', readonly=True, digits=(16, 2)),
        'prime':fields.float('Primes', readonly=True, digits=(16, 2)),
        'indemnite':fields.float('Indemnites', readonly=True, digits=(16, 2)),
        'avantage':fields.float('Avantages', readonly=True, digits=(16, 2)),
        'exoneration':fields.float('Exonerations', readonly=True, digits=(16, 2)),
        'deduction':fields.float('Deductions', readonly=True, digits=(16, 2)),
        'working_days' : fields.float('Jours travailles', size=64, digits=(16, 2)),
        'prime_anciennete' : fields.float('Prime anciennete', size=64, digits=(16, 2)),
        'frais_pro': fields.float('Frais professionnels', size=64, digits=(16, 2)),
        'personnes': fields.integer('Personnes'),
        'absence':fields.float('Absences', size=64, digits=(16, 2)),
        'arrondi':fields.float('Arrondi', size=64, digits=(16, 2)),
        'logement':fields.float('Logement', size=64, digits=(16, 2)),
        'prev_salaire_net': fields.function(_get_previous_salary, type='float', string='Salaire Net Precedent', method=True, store=False),
        'difference':fields.function(_get_salary_difference, type='float', string='Difference', method=True, store=False),
        }


    def _name_get_default(self, cr, uid, context=None):
            return self.pool.get('ir.sequence').get(cr, uid, 'hr.payroll_ma.bulletin')
    _defaults = {
        'name': _name_get_default,

    }
    def _check_unicite(self, cr, uid, ids):
           for unicite in self.browse(cr, uid, ids):
               unicite_id = self.search(cr, uid, [('period_id', '=', int(unicite.period_id)), ('employee_id', '=', int(unicite.employee_id)) ])
               if len(unicite_id) > 1:
                   return False
           return True

    _constraints = [
        (_check_unicite, u'Un bulletin de paie est repété pour un même employé', ['period', 'employee'])
        ]
    def onchange_contract_id(self, cr, uid, ids, contract_id):
        salaire_base = 0
        normal_hours = 0
        hour_base = 0
        if contract_id:
            contract = self.pool.get('hr.contract').browse(cr, uid, contract_id)
            salaire_base = contract.wage
            hour_base = contract.hour_salary
            normal_hours = contract.monthly_hour_number

        result = {'value': {
                            'salaire_base' : salaire_base,
                            'hour_base' : hour_base,
                            'normal_hours' : normal_hours,
                        }
                    }
        return result

    def onchange_employee_id(self, cr, uid, ids, employee_id, period_id):
        if not employee_id :
            return {}
        # id_payroll_ma = ids[0]
        # payroll_ma = pool.get('hr.payroll_ma').browse(cr, uid, id_payroll_ma)
        employee_contract_id = False
        partner_id = False
        date_begin = time.strftime('%Y-%m-%d'),
        salaire_base = 0
        normal_hours = 0
        hour_base = 0
        days = 0

        if not period_id:
            raise osv.except_osv(_(u'Période non définie !'), _(u"Vous devez d\'abord spécifier une période !"))
        if period_id and employee_id :

            period = self.pool.get('account.period').browse(cr, uid, period_id)
            # self.write(cr, uid, [bulletin.id], {'period_id' : payroll_ma.id })
            employee = self.pool.get('hr.employee').browse(cr, uid, employee_id)
            if not employee.contract_id:
                raise osv.except_osv(_(u'Pas de contrat !'), _(u"Vous devez d\'abord saisir un contrat pour  %s !") % employee.name)

            sql = '''select sum(number_of_days) from hr_holidays h
                left join hr_holidays_status s on (h.holiday_status_id=s.id)
                where date_from >= '%s' and date_to <= '%s'
                and employee_id = %s
                and state = 'validate'
                and s.payed=False''' % (period.date_start, period.date_stop, employee_id)
            cr.execute(sql)
            res = cr.fetchone()
            if res[0] == None:
                days = 0
            else :
                days = res[0]

            # for contract in employee.contract_ids :
            #    if date_begin and contract.date_start <= date_begin and \
            #    (contract.date_end and contract.date_end >= date_begin or not contract.date_end) :
            #        employee_contract_id = contract.id
            #        salaire_base = contract.wage
            #        hour_base = contract.hour_salary
            #        normal_hours = contract.monthly_hour_number
            diff = 0
            for contract in employee.contract_ids:
                ######Hari
                date_start_contrat_considere = 0
                date_end_contrat_considere = 0
                if period.date_start > contract.date_start:
                    if contract.date_end:
                        if contract.date_end > period.date_start:
                            date_start_contrat_considere = period.date_start
                            if contract.date_end > period.date_stop:
                                date_end_contrat_considere = period.date_stop
                                diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                                diff = diff.days + 1
                            elif contract.date_end < period.date_stop:
                                date_end_contrat_considere = contract.date_end
                                diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                                diff = diff.days + 1
                        elif contract.date_end == period.date_start:
                            if datetime.strptime(period.date_start, '%Y-%m-%d').weekday() in (5, 6):
                                diff = 0
                            else: diff = 1
                        elif contract.date_end < period.date_start:
                            diff = 0
                    else:
                        date_start_contrat_considere = period.date_start
                        date_end_contrat_considere = period.date_stop
                        diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                        diff = diff.days + 1
                elif period.date_start < contract.date_start:
                    if contract.date_start < period.date_stop:
                        date_start_contrat_considere = contract.date_start
                        if contract.date_end:
                            if contract.date_end > period.date_stop:
                                date_end_contrat_considere = period.date_stop
                                diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                                diff = diff.days + 1

                                ####
                            elif contract.date_end < period.date_stop:
                                date_end_contrat_considere = contract.date_end  # #utile pour cas prestataire
                                diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                                diff = diff.days + 1
                        else:
                            date_end_contrat_considere = period.date_stop
                            diff = datetime.strptime(date_end_contrat_considere, '%Y-%m-%d') - datetime.strptime(date_start_contrat_considere, '%Y-%m-%d')
                            diff = diff.days + 1
                    elif contract.date_start > period.date_stop:
                        diff = 0
                    elif contract.date_start == period.date_end:
                        if datetime.strptime(period.date_stop, '%Y-%m-%d').weekday() in (5, 6):
                            diff = 0
                        else: diff = 1

                        # if contract.date_ed > period.date_start:
                        # calcul date de fin pour lemois en cours

                    # diff=date_end(period.date_end) - date-start
                    # diff=datetime.strptime(period.date_end,'%Y-%m-%d')-datetime.strptime(period.date_start,'%Y-%m-%d')
                    # diff=diff.days+1
                ######Hari
                # if contract.date_end and contract.date_end >= period.date_start:
                    # diff=datetime.strptime(contract.date_end,'%Y-%m-%d')-datetime.strptime(period.date_start,'%Y-%m-%d')
                    # diff=diff.days+1
                # if contract.date_start > period.date_start:
                    # if contract.date_end and contract.date_end >= period.date_start:
                        # diff=datetime.strptime(contract.date_end,'%Y-%m-%d')-datetime.strptime(contract.date_start,'%Y-%m-%d')
                        # diff=diff.days+1
                    # else:
                        # diff=datetime.strptime(period.date_stop,'%Y-%m-%d')-datetime.strptime(contract.date_start,'%Y-%m-%d')
                        # diff=diff.days+1
            if diff > 0:
                days_work = int(diff)
            else:
                days_work = int(period.date_stop[8:10])
            sanction_type = self.pool.get('sanction.type')
            sanction_type_ids = sanction_type.search(cr, uid, [('days_work', '=', 'True')])
            sanction_obj = self.pool.get('hr.employee.sanction')
            sanctions = sanction_obj.search(cr, uid, [('name', '=', employee.id), ('type', 'in', sanction_type_ids), ('date_start', '>=', period.date_start)])
            sanctions = sanction_obj.browse(cr, uid, sanctions)
            for sanction in sanctions:
                diff = datetime.strptime(sanction.date_end, '%Y-%m-%d') - datetime.strptime(sanction.date_start, '%Y-%m-%d')
                diff = diff.days
                days_work -= diff
            result = {'value': {
                            'employee_contract_id' : employee.contract_id.id,
                            'salaire_base' : employee.contract_id.wage,
                            'hour_base' : employee.contract_id.hour_salary,
                            'normal_hours' : employee.contract_id.monthly_hour_number,
                            'working_days' : days_work - abs(days),
                            'period_id' : period_id
                        }
                    }

            return result

    def get_prime_assiduite_original(self, cr, uid, ids):
        # code = 16
        # name = '16 Prime assiduite'
        result = {}
        result['deductible'] = False,
        result['type'] = 'brute'
        rub_obj = self.pool.get('hr.payroll_ma.rubrique')
        rub_ids = rub_obj.search(cr, uid, [('code', '=', '16')])
        if len(rub_ids) != 0:
            rub_browse = rub_obj.browse(cr, uid, rub_ids[0])
        else:
            raise osv.except_osv(_('warning'), _('Cette rubrique n\'existe pas! \n Veuillez la definir SVP.'))

        result['name'] = str(rub_browse.code) + ' ' + str(rub_browse.name) + 'calculated'
        taux = 0
        montant = 0
        period_id = 0
        emp_obj = self.pool.get('hr.employee')
        emp_assiduite_obj = self.pool.get('hr.employee.assiduite')
        id_bulletin = ids[0]
        result['id_bulletin'] = id_bulletin
        bulletin = self.browse(cr, uid, id_bulletin)
        period_id = bulletin.period_id.id
        employee_id = bulletin.employee_id.id
        emp_browse = emp_obj.browse(cr, uid, employee_id)
        if emp_browse.assiduite:
            montant = emp_browse.amount_assiduite
            result['base'] = (montant)
        else:
            return False

        assiduite_ids = emp_assiduite_obj.search(cr, uid,
            [('employee_id', '=', employee_id), ('period_id', '=', period_id)])
        if len(assiduite_ids) != 0:
            for assiduite_id in assiduite_ids:
                taux = emp_assiduite_obj.browse(cr, uid, assiduite_id).rate_id.name
                montant = montant - (montant * taux / 100)
                result['rate_employee'] = float(100 - taux)  # /100
                result['subtotal_employee'] = montant
        else:
            result['rate_employee'] = 100
            result['subtotal_employee'] = montant

        return result


    def get_prime_assiduite_by_contract(self, cr, uid, ids):
        # code = 16
        # name = '16 Prime assiduite'
        result = {}
        result['deductible'] = False,
        result['type'] = 'brute'
        rub_obj = self.pool.get('hr.payroll_ma.rubrique')
        rub_ids = rub_obj.search(cr, uid, [('code', '=', '16')])
        if len(rub_ids) != 0:
            rub_browse = rub_obj.browse(cr, uid, rub_ids[0])
        else:
            raise osv.except_osv(_('warning'), _('Cette rubrique n\'existe pas! \n Veuillez la definir SVP.'))

        result['name'] = str(rub_browse.code) + ' ' + str(rub_browse.name) + 'calculated'
        taux = 0
        montant = 0
        period_id = 0
        contract_obj = self.pool.get('hr.contract')
        # contract_ids = contract_obj.search(cr,uid,[])

        emp_obj = self.pool.get('hr.employee')
        emp_assiduite_obj = self.pool.get('hr.employee.assiduite')
        id_bulletin = ids[0]
        result['id_bulletin'] = id_bulletin
        bulletin = self.browse(cr, uid, id_bulletin)

        contract_id = bulletin.employee_contract_id.id
        contract_browse = contract_obj.browse(cr, uid, contract_id)


        period_id = bulletin.period_id.id
        employee_id = bulletin.employee_id.id
        # emp_browse = emp_obj.browse(cr,uid,employee_id)
        if contract_browse.assiduite:
            montant = contract_browse.amount_assiduite
            result['base'] = (montant)
        else:
            return False

        assiduite_ids = emp_assiduite_obj.search(cr, uid,
            [('employee_id', '=', employee_id), ('period_id', '=', period_id)])
        if len(assiduite_ids) != 0:
            for assiduite_id in assiduite_ids:
                taux = emp_assiduite_obj.browse(cr, uid, assiduite_id).rate_id.name
                montant = montant - (montant * taux / 100)
                result['rate_employee'] = float(100 - taux)  # /100
                result['subtotal_employee'] = montant
        else:
            result['rate_employee'] = 100
            result['subtotal_employee'] = montant

        return result

    def get_prime_assiduite(self, cr, uid, ids):
        # code = 16
        # name = '16 Prime assiduite'
        result = {}
        # result['deductible'] = False,
        # result['type']='brute'

        bulletin_obj = self.browse(cr, uid, ids)
        contract_obj = bulletin_obj.employee_contract_id
        contract_id = contract_obj.id
        # raise osv.except_osv(_('warning'),_('contract_id = %s')%(contract_id))
        # bulletin_obj.employee_contract_id.id
        # test pour verifier si a droit prime assiduite
        assidue = contract_obj.assiduite
        taux = 0
        montant = 0
        period_id = 0
        id_bulletin = ids[0]
        emp_assiduite_obj = self.pool.get('hr.employee.assiduite')

        if contract_obj.assiduite:
            # raise osv.except_osv(_('warning'),_('assidue = %s')%(assidue))
            rub_obj = self.pool.get('hr.payroll_ma.rubrique')
            rub_ids = rub_obj.search(cr, uid, [('code', '=', '16')])
            if len(rub_ids) != 0:
                result['rubrique_id'] = rub_ids[0]
                montant = contract_obj.amount_assiduite
                result['montant'] = (montant)
                result['permanent'] = True
                rub_browse = rub_obj.browse(cr, uid, rub_ids[0])

            else:
                raise osv.except_osv(_('warning'), _('Cette rubrique n\'existe pas! \n Veuillez la definir SVP.'))

            ligne_rub_obj = self.pool.get('hr.payroll_ma.ligne_rubrique')
            current_contract_id = contract_obj.id
            current_employee_id = contract_obj.employee_id.id
            # raise osv.except_osv(_('warning'),_('contract = %s \n employee = %s')%(current_contract_id,current_employee_id))
            for c_obj_rub_line in contract_obj.rubrique_ids:
                # raise osv.except_osv(_('warning'),_('c_obj = %s')%(c_obj.rubrique_id.code))
                critere = [('id_contract', '=', current_contract_id),
                            ('employee_id', '=', current_employee_id),
                            ('rubrique_id', '=', result['rubrique_id'])]
                            # ('permanent','=',True)
                ligne_rub_ids = ligne_rub_obj.search(cr, uid, critere)
                if ligne_rub_ids != []:
                    ligne_rub_obj.write(cr, uid, ligne_rub_ids[0],
                        {'permanent':True, 'montant':result['montant']})
                else:
                    ligne_rub_obj.create(cr, uid,
                        {
                            'id_contract': c_obj_rub_line.id_contract.id,
                            'rubrique_id':result['rubrique_id'],
                            'permanent':True,
                            'montant':result['montant']
                        })
        else:
            return False
                # raise osv.except_osv(_('warning'),_('ligne_rub_ids = %s')%(ligne_rub_ids))
        #         rubrique_code = c_obj_rub_line.rubrique_id.id
        #         raise osv.except_osv(_('warning'),_('rubrique_code = %s')%(rubrique_code))
        #         ligne_rub_ids = ligne_rub_obj.search(cr,uid,[('id','=',c_obj.id)])
        #         if c_obj.rubrique_id.id == result['rubrique_id']:

        #             raise osv.except_osv(_('warning'),_('c_obj = %s')%(rubrique_code))

        #     # result['name'] = str(rub_browse.code)+' '+str(rub_browse.name)+'calculated'
        # # contract_obj = self.pool.get('hr.contract')
        # # contract_ids = contract_obj.search(cr,uid,[])

        # # emp_obj = self.pool.get('hr.employee')
        #     result['id_bulletin']=id_bulletin
        #     # bulletin = self.browse(cr,uid,id_bulletin)


        # # contract_browse = contract_obj.browse(cr,uid,contract_id)
        #     period_id = bulletin_obj.period_id.id
        #     employee_id = bulletin_obj.employee_id.id
        # # emp_browse = emp_obj.browse(cr,uid,employee_id)
        # # if contract_browse.assiduite:

        # else:
        #     return False

        # assiduite_ids = emp_assiduite_obj.search(cr,uid,
        #     [('employee_id','=',employee_id),('period_id','=',period_id)])
        # if len(assiduite_ids)!=0:
        #     for assiduite_id in assiduite_ids:
        #         taux = emp_assiduite_obj.browse(cr,uid,assiduite_id).rate_id.name
        #         montant = montant - (montant*taux/100)
        #         result['rate_employee'] = float(100-taux) #/100
        #         result['subtotal_employee'] = montant
        # else:
        #     result['rate_employee'] = 100
        #     result['subtotal_employee'] = montant

        # return result
        return True



    # La fonction pour le calcul du taux de la prime d'anciennete
    def get_prime_anciennete(self, cr, uid, ids):
        taux = 0
        id_bulletin = ids[0]
        bulletin = self.pool.get('hr.payroll_ma.bulletin').browse(cr, uid, id_bulletin)

        # date_salary = time.strftime('%Y-%m-%d')
        date_salary = bulletin.period_id.date_start
        # modification car deux date pour anciennete
        if bulletin.employee_id.date_bis == False:
            date_embauche = bulletin.employee_id.date
        else:
            date_embauche = bulletin.employee_id.date_bis
        # fin modification
        # date_embauche = bulletin.employee_id.date
        if bulletin.employee_id.anciennete:
            date_salary = date_salary.split('-')
            date_embauche = date_embauche.split('-')

            # jours1 = 0
            # jours2 = 0
            # jours1 = ((int(date_salary[0]) * 365) + (int(date_salary[1]) * 30) + int((date_salary[2])))
            # jours2 = ((int(date_embauche[0]) * 365) + (int(date_embauche[1]) * 30) + (int(date_embauche[2])))
            # anciennete = (jours1 - jours2) / 365
            anciennete = int(date_salary[0]) - int(date_embauche[0])
            objet_anciennete = self.pool.get('hr.payroll_ma.anciennete')
            id_anciennete = objet_anciennete.search(cr, uid, [])
            liste = objet_anciennete.read(cr, uid, id_anciennete, ['debuttranche', 'fintranche', 'taux'])
            anciennete = int(anciennete)
            # logger.notifyChannel('Anciennete', netsvc.LOG_INFO, anciennete)
            for tranche in liste:
                if(anciennete >= tranche['debuttranche']) and (anciennete < tranche['fintranche']):
                    taux = tranche['taux']

            return taux
        else:
            return 0.0

    ####La fonction pour la calcul de IGR
    def get_igr(self, cr, uid, ids, montant, cotisations):
        plafond_loyer = montant * 0.25
        plafond_total_avantage = montant * 0.2
        res = {}
        taux = 0
        somme = 0
        salaire_net_imposable = 0
        id_bulletin = ids[0]
        bulletin = self.pool.get('hr.payroll_ma.bulletin').browse(cr, uid, id_bulletin)

        # adv_amount est à comparer avec 20% de la somme acquise (element positive) et on prend le minimun entre les deux.
        personnes = bulletin.employee_id.chargefam
        logement = bulletin.employee_id.logement
        params = self.pool.get('hr.payroll_ma.parametres')
        ids_params = params.search(cr, uid, [])
        dictionnaire = params.read(cr, uid, ids_params[0])
        fraispro = montant * dictionnaire['fraispro'] / 100
        if fraispro < dictionnaire['plafond']:
            salaire_net_imposable = montant - fraispro - cotisations - logement
        else :
            salaire_net_imposable = montant - dictionnaire['plafond'] - cotisations - logement
        salaire_net_imposable = montant


        adv_obj = self.pool.get('hr.employee.advantage')
        advantages = adv_obj.search(cr, uid, [('state', '=', 'remove'), ('period_id', '=', bulletin.period_id.id), ('employee_id', '=', bulletin.employee_id.id)])
        adv_amount = 0
        T = 0  # Hari
        for adv in adv_obj.browse(cr, uid, advantages):
            adv_amount += (adv.amount * adv.name.rate * -1)
        salaire_net_imposable += min(adv_amount, montant * 0.20)
        salaire_net_imposable -= cotisations

        objet_ir = self.pool.get('hr.payroll_ma.ir')
        id_ir = objet_ir.search(cr, uid, [])
        liste = objet_ir.read(cr, uid, id_ir, ['debuttranche', 'fintranche', 'taux', 'somme'])
        # raise osv.except_osv(_('liste'),_('liste = %s \n salaire_net_imposable =%s')%(liste,salaire_net_imposable))


        for tranche in liste:
            if(salaire_net_imposable >= tranche['debuttranche'] / 12) and (salaire_net_imposable < tranche['fintranche'] / 12):
                taux = tranche['taux']
                somme = (tranche['somme'] / 12)
        # print salaire_net_imposable
        salaire_net_imposable = int(salaire_net_imposable) / 1000 * 1000
        ir_brute = (salaire_net_imposable - (somme * 12)) * taux / 100  # dictionnaire['charge']+
        # ir_brute = (salaire_net_imposable * taux / 100) - somme
        familycharge = personnes * dictionnaire['charge']
        # raise osv.except_osv(_('salaire_net_imposable'),_('salaire_net_imposable = %s')%(salaire_net_imposable))
        ir_net = 0
        if((ir_brute - (personnes * dictionnaire['charge'])) < 0):
            ir_net = 0
        else:
            ir_net = ir_brute - (personnes * dictionnaire['charge'])

        # raise osv.except_osv(_('ir_net'),_('ir_net = %s \n ir_brute = %s')%(ir_net,ir_brute))
        if not dictionnaire['credit_account_id']:
            raise osv.except_osv(_('Erreur de configuration !'), _('Compte Credit IRSA non Défini '))
        res = {'salaire_net_imposable':salaire_net_imposable,
             'taux':taux,
             'ir_net':ir_net,
             'credit_account_id':dictionnaire['credit_account_id'][0],
             'frais_pro' : fraispro,
             'personnes' : personnes
             }

        return res

    def compute_all_lines(self, cr, uid, ids, context={}):
        params = self.pool.get('hr.payroll_ma.parametres')
        ids_params = params.search(cr, uid, [])
        dictionnaire = params.read(cr, uid, ids_params[0])
        id_bulletin = ids[0]
        bulletin = self.pool.get('hr.payroll_ma.bulletin').browse(cr, uid, id_bulletin)
        period = bulletin.id_payroll_ma.period_id
        days_work = int(period.date_stop[8:10])
        self.write(cr, uid, [bulletin.id], {'period_id' : bulletin.id_payroll_ma.period_id.id})
        sql = '''
        DELETE from hr_payroll_ma_bulletin_line where id_bulletin = %s
        '''
        cr.execute(sql, (id_bulletin,))
        salaire_base = bulletin.salaire_base
        normal_hours = bulletin.normal_hours
        hour_base = bulletin.hour_base
        working_days = bulletin.working_days
        sundays = bulletin.sundays
        normal = bulletin.normal
        # custom ARO
        # Depasse_limit = False
        # if normal > 4800
        normal = bulletin.normal
        overtime = bulletin.overtime_hours
        absences = bulletin.absences
        nuit = bulletin.nuit
        nuit_extra = bulletin.nuit_extra
        ferie = bulletin.ferie
        extra = bulletin.overtime_hours
        salaire_brute = 0
        salaire_brute_imposable = 0
        salaire_net = 0
        salaire_net_imposable = 0
        cotisations_employee = 0
        cotisations_employer = 0
        prime = 0
        indemnite = 0
        avantage = 0
        exoneration = 0
        prime_anciennete = 0
        deduction = 0
        logement = 0
        frais_pro = 0
        personne = 0
        absence = 0
        arrondi = 0
        rub_maj = {}
        # appel de la method get_prime_assiduite()
        is_assidue = self.get_prime_assiduite(cr, uid, ids)

        if salaire_base :
            absence += salaire_base - (salaire_base * (bulletin.working_days / days_work))
            rub_maj[u'10'] = round(salaire_base * (bulletin.working_days / days_work), 2)
            salaire_base_line = {
                'name' : '10 Salaire de base', 'id_bulletin' : id_bulletin,
                'type' : 'brute', 'base' : round(salaire_base, 2),
                'rate_employee' : round((bulletin.working_days / days_work) * 100, 2),
                'subtotal_employee':round(salaire_base * (bulletin.working_days / days_work), 2),
                'deductible' : False,
               }
            salaire_brute += salaire_base * (bulletin.working_days / days_work)

            self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, salaire_base_line)
        if normal_hours :
            normale_hours_line = {
                'name' : 'Heures normales', 'id_bulletin' : id_bulletin, 'type' : 'brute', 'base' : normal_hours,
                'rate_employee' : hour_base, 'subtotal_employee':normal_hours * hour_base, 'deductible' : False,
                }
            salaire_brute += hour_base * (normal_hours)

            self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, normale_hours_line)

        salaire_brute_imposable = salaire_brute
        sql = '''
            SELECT r.code,l.montant,l.taux,r.name,r.categorie,r.type,r.formule,r.afficher,r.sequence,r.imposable,r.plafond,r.ir,r.anciennete,r.absence,r.debit_account_id,r.credit_account_id
            FROM hr_payroll_ma_ligne_rubrique l
            LEFT JOIN hr_payroll_ma_rubrique r on (l.rubrique_id=r.id)
            WHERE
            (l.id_contract=%s and l.permanent=True) OR
            (l.id_contract=%s and l.date_start <= %s and l.date_stop >= %s)
            order by r.sequence
            '''
        cr.execute(sql, (bulletin.employee_contract_id.id, bulletin.employee_contract_id.id, bulletin.period_id.date_start, bulletin.period_id.date_stop))
        rubriques = cr.dictfetchall()
        ir = salaire_brute_imposable
        anciennete = 0
        prime_assiduite = 0
        # raise osv.except_osv(_('rubriques'),_('rubriques = %s')%(rubriques))
        for rubrique in rubriques :
            if(rubrique['categorie'] == 'majoration'):
                if is_assidue and rubrique['code'] == u'16':
                    # traitement de la prime assiduité
                    taux_assiduite = 0
                    rate_employee = 0
                    subtotal_employee = 0
                    montant_assiduite = rubrique['montant']
                    emp_assiduite_obj = self.pool.get('hr.employee.assiduite')
                    assiduite_ids = emp_assiduite_obj.search(cr, uid,
                        [('employee_id', '=', bulletin.employee_id.id), ('period_id', '=', bulletin.period_id.id)])
                    if len(assiduite_ids) != 0:
                        for assiduite_id in assiduite_ids:
                            taux_assiduite = emp_assiduite_obj.browse(cr, uid, assiduite_id).rate_id.name
                            montant_assiduite = montant_assiduite - (montant_assiduite * taux_assiduite / 100)
                            rate_employee = float(100 - taux_assiduite)  # /100
                            subtotal_employee = montant_assiduite
                    else:
                        rate_employee = 100
                        subtotal_employee = montant_assiduite
                    rub_maj[rubrique['code']] = subtotal_employee
                    prime_assiduite = subtotal_employee
                    prime += subtotal_employee
                    # raise osv.except_osv(_('warning'),_('rub_maj = %s')%(rub_maj[rubrique['code']]))
                    majoration_line = {
                        'name' : rubrique['code'] + ' ' + rubrique['name'],
                        'id_bulletin' : id_bulletin, 'type' : 'brute',
                        'base' : rubrique['montant'], 'rate_employee' : rate_employee,
                        'subtotal_employee':subtotal_employee, 'deductible' : False,
                        'afficher' : rubrique['afficher'],
                        'credit_account_id':rubrique['credit_account_id'],
                        'debit_account_id':rubrique['debit_account_id']
                        }

                    self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, majoration_line)
                    # raise osv.except_osv(_('warning'),_('assiduite = %s')%(majoration_line))
                else:
                    if rubrique['formule'] :
                        try:
                            rubrique['montant'] = eval(str(rubrique['formule']))
                        except Exception, e:
                            raise osv.except_osv(_('Formule Error !'), _('Formule Error : %s ' % (e)))
                    taux = 1
                    if rubrique['type'] == 'absence':
                        rubrique['montant'] = rubrique['montant'] * -1
                    montant = rubrique['montant']

                    if rubrique['taux']:
                        taux = rubrique['taux']
                        montant = rubrique['montant'] * taux / 100
                    if rubrique['absence']:
                        taux = bulletin.working_days / days_work
                        montant = rubrique['montant'] * taux
                        taux = taux * 100
                        absence += rubrique['montant'] - montant
                    if rubrique['type'] == 'nuit':
                        montant = rubrique['montant'] * nuit / 173.33 * taux / 100
                    if rubrique['type'] == 'nuit_extra':
                        montant = rubrique['montant'] * nuit_extra / 173.33 * taux / 100
                    if rubrique['type'] == 'absence':
                        montant = rubrique['montant'] * absences / 173.33
                    if rubrique['type'] == 'dimanche':
                        montant = rubrique['montant'] / 173.33 * sundays * taux / 100
                    if rubrique['type'] == 'normal':
                        montant = rubrique['montant'] / 173.33 * normal * taux / 100
                    if rubrique['type'] == 'extra':
                        montant = rubrique['montant'] / 173.33 * extra * taux / 100
                    if rubrique['type'] == 'ferie':
                        montant = rubrique['montant'] / 173.33 * ferie * taux / 100

                    if rubrique['anciennete'] :
                        anciennete += montant
                    if rubrique['ir']:
                        if rubrique['plafond'] == 0:
                            ir += montant
                        elif montant <= rubrique['plafond']:
                            ir += montant
                        elif montant > rubrique['plafond']:
                            ir += montant - rubrique['plafond']
                    if not rubrique['imposable']:
                        if rubrique['plafond'] == 0:
                            exoneration += montant
                        elif montant <= rubrique['plafond']:
                            exoneration += montant
                        elif montant > rubrique['plafond']:
                            exoneration += rubrique['plafond']
                            salaire_brute_imposable += montant - rubrique['plafond']
                    if rubrique['type'] in ('nuit', 'nuit_extra', 'extra', 'absence', 'dimanche', 'prime', 'normal', 'ferie'):
                            prime += montant
                    elif rubrique['type'] == 'indemnite':
                            indemnite += montant
                    elif rubrique['type'] == 'avantage':
                            avantage += montant
                    rub_maj[rubrique['code']] = montant
                    majoration_line = {
                    'name' : rubrique['code'] + ' ' + rubrique['name'], 'id_bulletin' : id_bulletin, 'type' : 'brute', 'base' : rubrique['montant'],
                     'rate_employee' : taux , 'subtotal_employee':montant, 'deductible' : False, 'afficher' : rubrique['afficher'],
                      'credit_account_id':rubrique['credit_account_id'], 'debit_account_id':rubrique['debit_account_id']
                        }

                    self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, majoration_line)

        # ajoute anciennete dans le bulletin
        taux_anciennete = self.get_prime_anciennete(cr, uid, ids) / 100

        prime_anciennete = (salaire_base) * taux_anciennete * bulletin.working_days / days_work
        rub_maj[u'13'] = prime_anciennete

        if taux_anciennete :
            anciennete_line = {
                'name' : '13 Prime danciennete', 'id_bulletin' : id_bulletin, 'type' : 'brute',
                'base' : (salaire_base * bulletin.working_days / days_work), 'rate_employee' : taux_anciennete, 'subtotal_employee':prime_anciennete,
                'deductible' : False,
                }
            self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, anciennete_line)

        salaire_brute += prime + indemnite + avantage + prime_anciennete  # + prime_assiduite
        # raise osv.except_osv(_('sal_brute'),_('sal_brute = %s \n prime = %s')%(salaire_brute,prime))
        salaire_brute_imposable = salaire_brute - exoneration
        cotisations = bulletin.employee_contract_id.cotisation.cotisation_ids
        # raise osv.except_osv(_('rub_maj'),_('rub_maj = %s')%(rub_maj))
        base = 0
        cot_ir = 0
        if bulletin.employee_id.affilie:
            all_coti = []
            for cot in cotisations :
                if cot.plafonee and salaire_brute_imposable >= cot.plafond:
                    base = cot.plafond
                else : base = salaire_brute_imposable
                if cot.rubriques:
                    cot_rub = cot.rubriques.split(',')
                    base = 0
                    _logger.info(rub_maj)
                    for c in cot_rub:
                        if c in rub_maj:
                            base = base + rub_maj[c]
                            _logger.info(cot.name)
                            _logger.info(c)
                            _logger.info(rub_maj[c])
                            _logger.info(base)
                    _logger.info(base)
                rub_maj[cot.code] = base * cot.tauxsalarial / 100 * (-1)
                cotisation_line = {
                'name' : cot.code + ' ' + cot.name, 'id_bulletin' : id_bulletin, 'type' : 'cotisation',
                'base' : base ,
                'rate_employee' : cot.tauxsalarial,
                'rate_employer' : cot.tauxpatronal,
                'subtotal_employee':base * cot.tauxsalarial / 100 ,
                'subtotal_employer':base * cot.tauxpatronal / 100,
                'credit_account_id': cot.credit_account_id.id,
                'debit_account_id' : cot.debit_account_id.id,
                'deductible' : True,
                }
                all_coti.append(cotisation_line)  # debug
                cotisations_employee += base * cot['tauxsalarial'] / 100
                cotisations_employer += base * cot['tauxpatronal'] / 100
                self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, cotisation_line)
                if cot.ir:
                    cot_ir = cot_ir + base * cot.tauxsalarial / 100
                if cot.plafond_tri:
                    mois = bulletin.period_id.date_stop[5:7]
                    if int(mois) % 3 == 0:
                        mois_dernier = 0
                        actuel = base * cot['tauxsalarial'] / 100
                        old_period = []
                        old_period.append(int(bulletin.period_id.id) - 1)
                        old_period.append(int(bulletin.period_id.id) - 2)
                        old_bulletins = self.pool.get('hr.payroll_ma.bulletin').search(cr, uid, [('employee_id', '=', bulletin.employee_id.id), ('period_id', 'in', old_period)])
                        old_bulletins = self.pool.get('hr.payroll_ma.bulletin').browse(cr, uid, old_bulletins)
                        for old_bulletin in old_bulletins:
                            for ol in old_bulletin.salary_line_ids:
                                if ol.name == cot.name:
                                    mois_dernier += ol.subtotal_employee
                        total = actuel + mois_dernier
                        plafond_trimestre = cot.plafond * cot.tauxsalarial / 100 * 3

                        if total > plafond_trimestre:
                            ajustement = total - plafond_trimestre
                            cotisation_line2 = {
                            'name' : cot.name + ' - Ajustement', 'id_bulletin' : id_bulletin, 'type' : 'cotisation', 'base' : ajustement,
                            'rate_employee' : 100, 'rate_employer' : 0,
                            'subtotal_employee':0 - ajustement,
                            'subtotal_employer':0,
                            'credit_account_id': cot.credit_account_id.id,
                            'debit_account_id' : cot.debit_account_id.id,
                            'deductible' : True,
                            }
                            cotisations_employee -= ajustement
                            self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, cotisation_line2)
            # raise osv.except_osv(_('all_coti'),_('all_coti = %s')%(all_coti)) #debug


            ###############Import sur le revenu
        # prime_assiduite = rub_maj[u'16']
        montant_igr = ir + prime_anciennete + prime_assiduite
        # raise osv.except_osv(_('igr'),_('prime_assiduite = %s')
        #     %(prime_assiduite))

        res = self.get_igr(cr, uid, ids, montant_igr, cot_ir)
        ir_line = {
                'name' : '62 RETENUE I.G.R.', 'id_bulletin' : id_bulletin, 'type' : 'cotisation', 'base' : res['salaire_net_imposable'], 'rate_employee' : res['taux'],
                'subtotal_employee':res['ir_net'], 'credit_account_id': res['credit_account_id'], 'debit_account_id' : res['credit_account_id'], 'deductible' : True,
                }
        self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, ir_line)
        for rubrique in rubriques :
            # print rubrique['categorie']
            if(rubrique['categorie'] == 'deduction'):
                    deduction += rubrique['montant']
                    deduction_line = {
                    'name' :rubrique['code'] + ' ' + rubrique['name'], 'id_bulletin' : id_bulletin, 'type' : 'retenu', 'base' : rubrique['montant'],
                    'rate_employee' : 100, 'subtotal_employee':rubrique['montant'], 'deductible' : True, 'afficher' : rubrique['afficher'],
                    'credit_account_id':rubrique['credit_account_id'], 'debit_account_id':rubrique['debit_account_id']
                   }
                    self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, deduction_line)
        salaire_net = salaire_brute - res['ir_net'] - cotisations_employee - deduction
        salaire_net_a_payer = salaire_brute - deduction - res['ir_net'] - cotisations_employee
        # print '>>>>>>>>>>>>>>>>>>>salaire net'
        # print salaire_net_a_payer
        # print salaire_brute
        # print deduction
        # print res['ir_net']
        # print cotisations_employee
        arrondi = (round(salaire_net_a_payer, 2) - int(salaire_net_a_payer))  # 1-
        # code original
        # if  arrondi !=1:
            # arrondi=1-(salaire_net_a_payer-int(salaire_net_a_payer))
            # salaire_net_a_payer+=arrondi
            # arrondi_line= {
                        # 'name' : 'Arrondi', 'id_bulletin' : id_bulletin, 'type' : 'retenu','base' : arrondi,
                        # 'rate_employee' : 100, 'subtotal_employee':arrondi, 'deductible' : True,
                       # }

            # self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, arrondi_line)
        # else :arrondi =0
        # code rectifier
        # <
        # if  arrondi >= 0.5:
        #     arrondi=1
        #     sn=int(salaire_net_a_payer)
        #     salaire_net_a_payer=sn+arrondi
        #     arrondi_line= {
        #                 'name' : 'Arrondi', 'id_bulletin' : id_bulletin, 'type' : 'retenu','base' : arrondi,
        #                 'rate_employee' : 100, 'subtotal_employee':arrondi, 'deductible' : True,
        #                }

        #     self.pool.get('hr.payroll_ma.bulletin.line').create(cr, uid, arrondi_line)
        # else :arrondi =0
        arrondi = 0
        salaire_net += arrondi
        self.write(cr, uid, [bulletin.id], {   'salaire_brute' : salaire_brute,
                                               'salaire_brute_imposable':salaire_brute_imposable,
                                               'salaire_net':salaire_net,
                                               'salaire_net_a_payer':salaire_net_a_payer,
                                               'salaire_net_imposable':res['salaire_net_imposable'],
                                               'cotisations_employee':cotisations_employee,
                                               'cotisations_employer':cotisations_employer,
                                               'igr':res['ir_net'],
                                               'prime':prime,
                                               'indemnite':indemnite,
                                               'avantage':avantage,
                                               'deduction':deduction,
                                               'prime_anciennete':prime_anciennete,
                                               'exoneration':exoneration,
                                               'absence':absence,
                                               'frais_pro':res['frais_pro'],
                                               'personnes':res['personnes'],
                                               'arrondi' : arrondi,
                                               'logement' : bulletin.employee_id.logement
                                                })


        return True

hr_payroll_ma_bulletin()


class hr_rubrique(osv.osv):
    _name = "hr.payroll_ma.rubrique"
    _description = "rubrique"
    _columns = {
        'credit_account_id': fields.many2one('account.account', 'Credit account', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'debit_account_id': fields.many2one('account.account', 'Debit account', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'name' : fields.char('Nom de la rubrique', size=64, required="True"),
        'code':fields.char('Code', size=64, required=False, readonly=False),
        'categorie' : fields.selection([('majoration', 'Majoration'), ('deduction', 'Deduction'),
             ], 'Categorie'),
        'sequence': fields.integer('Sequence', help='Ordre d\'affichage dans le bulletin de paie'),
        'type':fields.selection([
            ('prime', 'Prime'),
            ('indemnite', 'Indemnite'),
            ('avantage', 'Avantage'),
            ('nuit', 'Majoration de Nuit'),
            ('dimanche', 'Majoration de Dimanche'),
            ('absence', 'Absence'),
            ('normal', 'HS Normal'),
            ('extra', 'HS Extra'),
            ('ferie', 'HS Ferie'),
            ('nuit_extra', 'Nuit Ferie')
             ], 'Type'),
        'plafond':fields.float('Plafond exonere'),
        'formule':fields.char('Formule', size=64, required=False, help='''
        Pour les rubriques de type majoration on utilise les variables suivantes :
            salaire_base : Salaire de base
            hour_base : Salaire de l heure
            normal_hours : Les heures normales
            working_days : Jours travalles (imposable)
        '''),
        'imposable':fields.boolean('Imposable', required=False),
        'afficher':fields.boolean('Afficher', required=False, help='afficher cette rubrique sur le bulletin de paie'),
        'ir' :fields.boolean('IR', required=False),
        'anciennete' :fields.boolean('Anciennete', required=False),
        'absence' :fields.boolean('Absence', required=False),
        'note' : fields.text('Commentaire'),
        'prix' : fields.float('Prix'),
        'quantite' : fields.float('Quantite'),
        'rappel_rubrique_id':fields.many2one('hr.payroll_ma.rubrique', 'Rappel de Rubrique'),
                }
    _defaults = {
        'sequence': lambda * a: 1,
        'anciennete': lambda * a: True,
        'absence': lambda * a: True,
        'imposable': lambda * a: False,
        'afficher': lambda * a: True,
        'type': lambda * a: 'prime',
        'categorie': lambda * a: 'majoration',

    }

    _order = 'code'

    def name_get(self, cr, uid, ids, context={}):
        if not len(ids):
            return []
        res = []
        for rub in self.browse(cr, uid, ids, context=context):
            res.append((rub.id, rub.code + ' ' + rub.name))
        return res

    def name_search(self, cr, uid, name='', args=None, operator='ilike', context=None, limit=80):
        if not args:
            args = []
        if not context:
            context = {}
        ids = False
        if len(name) == 2:
            ids = self.search(cr, uid, [('code', 'ilike', name)] + args,
                    limit=limit, context=context)
        if not ids:
            ids = self.search(cr, uid, [('name', operator, name)] + args,
                    limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

hr_rubrique()

class hr_ligne_rubrique(osv.osv):

    def _sel_rubrique(self, cr, uid, context=None):
        obj = self.pool.get('hr.payroll_ma.rubrique')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['name', 'id'], context)
        res = [(r['id'], r['name']) for r in res]
        return res
    _name = "hr.payroll_ma.ligne_rubrique"
    _description = "Ligne Rubrique"
    _columns = {
        'rubrique_id' : fields.many2one('hr.payroll_ma.rubrique', 'Rubrique', selection=_sel_rubrique),
        'id_contract': fields.many2one('hr.contract', 'Ref Contrat', ondelete='cascade', select=True),
        'employee_id':fields.related('id_contract', 'employee_id', type='many2one', relation='hr.employee', store=True),
        'montant' : fields.float('Montant'),
        'taux' : fields.float('Taux'),
        'period_id': fields.many2one('account.period', 'Periode', domain=[('state', '<>', 'done')]),
        'permanent' : fields.boolean('Rubrique Permanante'),
        'date_start': fields.date('Date debut'),
        'date_stop': fields.date('Date fin'),
        'note' : fields.text('Commentaire'),
        'prix' : fields.float('Prix'),
        'name':fields.char('Description', 32),
        'quantite' : fields.text('Quantite'),
        'parameter_id': fields.many2one('hr.payroll_ma.parametres', 'Parametre', ondelete='cascade', select=True),

                }
    def _check_date(self, cr, uid, ids):
           for obj in self.browse(cr, uid, ids):
               if obj.date_start > obj.date_stop :
                   return False
           return True
    _order = 'date_start'
    _constraints = [
        (_check_date, 'Date debut doit etre inferieur a date fin', ['date_stop'])
        ]

    def onchange_rubrique_id(self, cr, uid, ids, rubrique_id):
        rubrique = self.pool.get('hr.payroll_ma.rubrique').browse(cr, uid, rubrique_id)

        result = {'value': {
                            'montant' : rubrique.plafond,
                        }
                    }

        return result
    def onchange_period_id(self, cr, uid, ids, period_id=False):
        result = {}
        if period_id :
            period = self.pool.get('account.period').browse(cr, uid, period_id)
            result = {'value': {
                            'date_start' :   period.date_start,
                            'date_stop' : period.date_stop
                            }
                    }

        return result

    def create_small_expenses(self, cr, uid, ids, context=None):
        small_expenses_obj = self.pool.get('small.expenses')
        payment_type = self.pool.get('account.voucher.type').search(cr, uid, [('name', '=', 'AVANCE SUR SALAIRE')])
        payment_type = self.pool.get('account.voucher.type').browse(cr, uid, payment_type)[0]

        for contract in self.browse(cr, uid, ids):
            data = {
               'name':'Avance sur salaire ',
               'create':uid,
               # 'beneficiary':contract.id_contract.employee_id.id,
               'date':str(datetime.now().date()),
               'amount':contract.montant,
               'payment_type_id':payment_type.id,
               'state':'auth',
            }
            result = small_expenses_obj.create(cr, uid, data)
        return {'warning':'Depense Cree'}

hr_ligne_rubrique()


class hr_payroll_ma_bulletin_line(osv.osv):

    # def _amount_employer(self, cr, uid, ids, prop, unknow_none,unknow_dict):
    #    res = {}
    #    for line in self.browse(cr, uid, ids):
    #        res[line.id] = round(float(line.base) * float(line.rate_employer),2)
    #    return res

    # def _amount_employee(self, cr, uid, ids, prop, unknow_none,unknow_dict):
    #    res = {}
    #    for line in self.browse(cr, uid, ids):
    #        res[line.id] = round(float(line.base) * float(line.rate_employee),2)
    #    return res


    _name = "hr.payroll_ma.bulletin.line"
    _description = "ligne de salaire"
    _columns = {
        'name': fields.char('Description', size=256, required=True),
        'id_bulletin': fields.many2one('hr.payroll_ma.bulletin', 'Ref Salaire', ondelete='cascade', select=True),
        'type' : fields.selection([('other', 'Autre'), ('retenu', 'Retenu'), ('cotisation', 'Cotisation'), ('brute', 'Salaire brute')], 'Type'),
        'credit_account_id': fields.many2one('account.account', 'Credit account', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'debit_account_id': fields.many2one('account.account', 'Debit account', domain=[('type', '<>', 'view'), ('type', '<>', 'closed')], help="The income or expense account related to the selected product."),
        'base': fields.float('Base', required=True, digits=(16, 2)),
        'subtotal_employee': fields.float('Montant Employe', digits=(16, 2)),
        'subtotal_employer': fields.float('Montant Employeur', digits=(16, 2)),
        'rate_employee' : fields.float('Taux Employe', digits=(16, 2)),
        'rate_employer' : fields.float('Taux Employeur', digits=(16, 2)),
        # 'quantity': fields.float('Quantity', required=True),
        'note': fields.text('Notes'),
        'deductible' : fields.boolean('deductible'),
        'afficher' : fields.boolean('Afficher'),
    }
    _defaults = {
        'afficher': lambda *a: True,
        'deductible' : lambda * a: False,
    }
    _order = 'name'

hr_payroll_ma_bulletin_line()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
