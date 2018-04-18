# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
import datetime
from dateutil import relativedelta
import calendar
from openerp.osv import osv, fields
from openerp.tools.translate import _
import logging
_logger = logging.getLogger(__name__)

class hr_salary_proposal(osv.osv):

    _name = "hr.salary.proposal"
    _description = "Proposition de salaire"
    _columns = {
        'date':fields.date('Date'),
        'name': fields.many2one('account.period', 'Periode applicable', required=True),
        'start': fields.many2one('account.period', 'Periode effet'),
        'salary_line':fields.one2many('hr.salary.proposal.line', 'proposal_id', 'Nouvelle Grille'),

        }
    _order = "name desc"

    def validate (self, cr, uid, ids, context=None):
        """ Function doc """
        contract_obj = self.pool.get('hr.contract')
        rubrique_obj = self.pool.get('hr.payroll_ma.ligne_rubrique')
        salary_line_obj = self.pool.get('hr.salary.proposal.line')
        rubrique_objt = self.pool.get('hr.payroll_ma.rubrique')  # new line
        diff = 1
        for proposal in self.browse(cr, uid, ids):
            for line in proposal.salary_line:
                date_start = datetime.datetime.strptime(proposal.name.date_start, '%Y-%m-%d')
                # _logger.info(line.contract_id.rubrique_ids)
                contract_info = contract_obj.copy(cr, uid, line.contract_id.id,
                    default={'date_start':date_start, 'wage':line.salary_proposal})
                perc = {}
                amt = {}
                rubriques = []
                for rub in line.rubrique_ids:
                    perc[rub.name.id] = rub.perc_increase
                    amt[rub.name.id] = rub.amount_increase
                    rubriques.append(rub.name.id)
                for rubrique in line.contract_id.rubrique_ids:                    
                    if rubrique.rubrique_id.id in rubriques:
                        amount = rubrique.montant + (rubrique.montant * perc[rubrique.rubrique_id.id] / 100) + amt[rubrique.rubrique_id.id]
                        amount_arrondi = int(amount / 10)  # * 10
                        reste_arrondi = amount % 10
                        if reste_arrondi >= 5:
                            amount_arrondi += 1
                        amount_arrondi = amount_arrondi * 10
                        amount = amount_arrondi
                        amount_diff = amount - rubrique.montant
                        rubrique_obj.copy(cr, uid, rubrique.id, default={'id_contract':contract_info, 'montant':amount, })
                        if proposal.start:
                            date1 = datetime.datetime.strptime(proposal.start.date_start, '%Y-%m-%d')
                            date2 = datetime.datetime.strptime(proposal.name.date_start, '%Y-%m-%d')
                            r = relativedelta.relativedelta(date2, date1)
                            diff = r.months
                            amount = amount_diff * diff
                            rubrique_obj.copy(cr, uid, rubrique.id,
                                default={'rubrique_id':rubrique.rubrique_id.rappel_rubrique_id.id,
                                        'id_contract':contract_info,
                                        'montant':amount, 'permanent':False,
                                        'date_stop':datetime.datetime.strptime(proposal.name.date_stop, '%Y-%m-%d'),
                                        'date_start':datetime.datetime.strptime(proposal.name.date_start, '%Y-%m-%d')
                                        })
                    else:
                        rubrique_obj.copy(cr, uid, rubrique.id, default={'id_contract':contract_info})
                # rappel saleire de base si il y avait augmentation
                # rubrique_obj.copy(cr,uid,rubrique.id,
                #                 default={ 'rubrique_id':rubrique.rubrique_id.rappel_rubrique_id.id,
                #                 'id_contract':contract_info,'montant':amount,'permanent':False,
                #                 'date_stop':datetime.datetime.strptime(proposal.name.date_stop,'%Y-%m-%d'),
                #                 'date_start':datetime.datetime.strptime(proposal.name.date_start,'%Y-%m-%d')})
                ################################################################################################
                T = False
                if line.wage != line.salary_proposal:
                    T = True
                if T:
                    # rubrique_objt = self.pool.get('hr.payroll_ma.rubrique')
                    rubrique_id = rubrique_objt.search(cr, uid, [('code', '=', '02')])  # id du rubrique rappel base
                    if len(rubrique_id) == 0:
                        raise osv.except_osv(_('Error'), _('This rubrique doesn\'t exist! \n create it! His code is: 02'))
                    amount = line.wage * (line.perc_increase / 100) * diff
                    new_rub_base = rubrique_obj.create(cr, uid, {'rubrique_id':rubrique_id[0],
                        'id_contract':contract_info,
                        'montant':amount, 'permanent':False,
                        'date_stop':datetime.datetime.strptime(proposal.name.date_stop, '%Y-%m-%d'),
                        'date_start':datetime.datetime.strptime(proposal.name.date_start, '%Y-%m-%d')})
                ################################################################################################
                new_contract = contract_info
                salary_line_obj.write(cr, uid, line.id, {'new_contract_id':new_contract})
hr_salary_proposal()

class hr_salary_proposal_line(osv.osv):

    _name = "hr.salary.proposal.line"
    _description = "Nouvelle Grille"
    
    def _get_perc(self, cr, uid, ids, name, arg, context={}):
        result = {}
        for payroll in self.browse(cr, uid, ids, context):
            net = 0
            if payroll.wage == 0:
                if payroll.name.id:
                    raise osv.except_osv(_('Warning'),
                                        _('le salaire de base du matricule %s est egale a zero! \n Veuillez rectifier cela dans son contrat!') % (payroll.name.matricule))
                else:
                    raise osv.except_osv(_('Warning'), _('Veuillez supprimer cette ligne de proposition et regenerer SVP!'))
            else:
                result[payroll.id] = (payroll.salary_proposal - payroll.wage) / payroll.wage * 100
        return result    
    _columns = {
        'name':fields.related('contract_id', 'employee_id', type='many2one', relation='hr.employee', string='Employe'),
        'contract_id':fields.many2one('hr.contract', 'Contrat'),
        'rubrique_ids':fields.one2many('rub.update.line', 'proposal_line_id', 'Ligne de proposition'),
        'new_contract_id':fields.many2one('hr.contract', 'Nouveau contrat'),
        'wage':fields.related('contract_id', 'wage', type='float', string='Salaire Actuel'),
        'salary_proposal':fields.float('Salaire Proposé'),
        'proposal_id':fields.many2one('hr.salary.proposal', 'Proposition'),
        'perc_increase':fields.function(_get_perc, method=True, type='float', digits=(16, 2), string='% Augmentation'),
        }   
hr_salary_proposal_line()

class rub_update_line(osv.TransientModel):
    _name = "rub.update.line"
    _columns = {
        'proposal_line_id':fields.many2one('hr.salary.proposal.line', 'Ligne de proposition'),
        'name':fields.many2one('hr.payroll_ma.rubrique', 'Rubrique'),
        'perc_increase': fields.float('Pourcentage augmentation', required=True),
        'amount_increase': fields.float('Montant augmentation', required=True),
        }
    _order = 'name'
rub_update_line()


class hr_contract_mod_wiz(osv.TransientModel):
    _name = 'hr.contract.mod.wiz'
    _description = 'Mis a jour salaire en masse'
    _columns = {
        'date': fields.date('Date', required=True),
        'perc_increase': fields.float('Pourcentage augmentation', required=True),
        'amount_increase': fields.float('Montant augmentation', required=True),
        'start': fields.many2one('account.period', 'Date effet'),  # Rétro-actif depuis               
        'period_id': fields.many2one('account.period', 'Periode applicable', required=True, domain=[('date_start', '>', datetime.date.today().strftime('%Y-01-01'))]),
        'employee_ids': fields.many2many('hr.employee', 'cont_dept_emp_rel', 'sum_id', 'emp_id', 'Employee(s)', domain=[('active', '=', True)]),
        'rubrique_ids':fields.one2many('rubrique.line.wiz', 'cont_mod_id', 'Rubriques'),
        }

    def generate(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [])[0]
        # raise osv.except_osv(_('data'),_('data = %s')%(data))
        contract_obj = self.pool.get('hr.contract')
        period_obj = self.pool.get('account.period')
        proposal_obj = self.pool.get('hr.salary.proposal')
        proposal_line_obj = self.pool.get('hr.salary.proposal.line')
        period_id = period_obj.browse(cr, uid, [data['period_id'][0]])[0]
        start = period_obj.browse(cr, uid, [data['start'][0]])[0]
        prev_period_id = period_obj.browse(cr, uid, [data['period_id'][0] - 1])[0]
        rub_line_obj = self.pool.get('rub.update.line')
        ############################################################
        # if data:
        #    raise osv.except_osv(_('data'), _('%s')%data)
        v = data['period_id'][0]
        period_id = period_obj.browse(cr, uid, [v])[0]  # periode de paie et return an object type class
        start = period_obj.browse(cr, uid, [data['start'][0]])[0]  # periode pour les rappels
        # prev_period_id=period_obj.browse(cr,uid,[data['period_id'][0]-1])[0]
        
        created = []
        if not data['employee_ids']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Employee. And try again'))
        proposal = proposal_obj.search(cr, uid, [('name', '=', period_id.id)])  # return list of result
        if proposal == []:
            proposal = proposal_obj.create(cr, uid,
                    {'name':period_id.id, 'start':start.id, 'date':datetime.date.today().strftime('%Y-%m-%d')})
        else:
            proposal = proposal[0]
        created.append(proposal)  # "id du proposition salariale (list) identifier par la période"
        date_today = datetime.date.today().strftime('%Y-%m-%d')
        contract_ids1 = contract_obj.search(cr, uid,
                    [('employee_id', 'in', data['employee_ids']),
                    '|', ('date_end', '=', False), ('date_end', '>=', date_today)])  # ou date_end est dans le futur(> today)
        contract_ids = contract_obj.read(cr, uid, contract_ids1, ['wage'])
        # raise osv.except_osv(_('contract_ids'),_('contract_ids = %s \n contract_ids1 = %s')%(contract_ids,contract_ids1))
        for contract in contract_ids:
            proposal_line = proposal_line_obj.search(cr, uid,
                    [('proposal_id', '=', created[0]), ('contract_id', '=', contract['id'])])
            if proposal_line == []:
                wage = contract['wage'] + (contract['wage'] * (data['perc_increase']) / 100) + data['amount_increase']
                pl = proposal_line_obj.create(cr, uid,
                        {'contract_id':contract['id'], 'salary_proposal':wage, 'proposal_id':created[0]})
                rubrique_lines = self.pool.get('rubrique.line.wiz').browse(cr, uid, data['rubrique_ids'])
                for rubrique in rubrique_lines:      
                    rub = {'proposal_line_id':pl,
                        'name':rubrique.name.id,
                        'perc_increase': rubrique.perc_increase,
                        'amount_increase': rubrique.amount_increase,
                        }
                    rub_line_obj.create(cr, uid, rub)
            else:
                wage = 0
                pl = 0
                if data['perc_increase'] != 0 or data['amount_increase'] != 0:
                    wage = contract['wage'] + (contract['wage'] * (data['perc_increase']) / 100) + data['amount_increase']
                    pl = proposal_line_obj.write(cr, uid, proposal_line[0],
                        {'contract_id':contract['id'], 'salary_proposal':wage, 'proposal_id':created[0]})
                else:
                    pl = proposal_line_obj.write(cr, uid, proposal_line[0],
                        {'contract_id':contract['id'], 'proposal_id':created[0]})
                # pl=proposal_line_obj.write(cr,uid,proposal_line[0],{'contract_id':contract['id'],'salary_proposal':wage,'proposal_id':created[0]})
                rubrique_lines = self.pool.get('rubrique.line.wiz').browse(cr, uid, data['rubrique_ids'])
                for rubrique in rubrique_lines:
                    condition = [('name', '=', rubrique.name.id), ('proposal_line_id', '=', proposal_line[0])]
                    search_id = rub_line_obj.search(cr, uid, condition)
                    rub = {'proposal_line_id':proposal_line[0],
                        'name':rubrique.name.id,
                        'perc_increase': rubrique.perc_increase,
                        'amount_increase': rubrique.amount_increase,
                        }
                    is_rub_exist = False
                    if len(search_id) == 0:
                        is_rub_exist = False
                    else:
                        is_rub_exist = True
                    if not is_rub_exist:
                        rub_line_obj.create(cr, uid, rub)
                    else:
                        rub_line_obj.write(cr, uid, search_id[0], rub)

        ##################################################
        # test={
        #    'domain': "[('id','in', ["+','.join(map(str,created))+"])]",
        #    'name': 'Contrats',
        #    'view_type': 'form',
        #    'view_mode': 'tree,form',
        #    'res_model': 'hr.salary.proposal',
        #    'view_id': False,
        #    'type': 'ir.actions.act_window',
        # }
        
        # if test:
        #    raise osv.except_osv(_('test'), _('%s')%test)
        ##################################################

        return {
            'domain': "[('id','in', [" + ','.join(map(str, created)) + "])]",
            'name': 'Contrats',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.salary.proposal',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }

        
    def _from_date(self, cursor, user, context={}):
        return datetime.date.today().strftime('%Y-%m-%d');


    _defaults = {
        'date': _from_date, }

hr_contract_mod_wiz()

class rubrique_line_wiz(osv.TransientModel):

    _name = "rubrique.line.wiz"
    _columns = {
        'cont_mod_id':fields.many2one('hr.contract.mod.wiz', 'Contract'),
        'name':fields.many2one('hr.payroll_ma.rubrique', 'Rubrique'),
        'perc_increase': fields.float('Pourcentage augmentation', required=True),
        'amount_increase': fields.float('Montant augmentation', required=True),
        }
    
rubrique_line_wiz()

class hr_salary_proposal_validate(osv.TransientModel):
    _name = "hr.salary.proposal.validate"
    _description = "Validation Proposition salariale"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):

        if context is None:
            context = {}
        res = super(hr_salary_proposal_validate, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        return res

    def validate_proposal(self, cr, uid, ids, context=None):

        rub_obj = self.pool.get('rub.update.line')
        prop_obj = self.pool.get('hr.salary.proposal')
        prop_line_obj = self.pool.get('hr.salary.proposal.line')
        
        
        active_ids = context['active_ids']
        props = []
        prop_line = rub_obj.read(cr, uid, active_ids, ['proposal_line_id'])
        for pl in prop_line:
            # _logger.info(pl)
            # _logger.info(pl['proposal_line_id'])
            props.append(pl['proposal_line_id'][0])
        proposals = prop_line_obj.read(cr, uid, props, ['proposal_id'])
        props = []
        for proposal in proposals:
            # _logger.info(proposal)
            if proposal['proposal_id'][0] not in props:
                props.append(proposal['proposal_id'][0])
        prop_obj.validate(cr, uid, props)
        return {}
        
    def cancel_planning(self, cr, uid, ids, context=None):
        """
        """
        planning_obj = self.pool.get('hr.employee.overtime')
        planning_obj.write(cr, uid, context['active_ids'], {'state':'refuse'})
        return {}
hr_salary_proposal_validate()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
