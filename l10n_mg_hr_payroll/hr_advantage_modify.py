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

class hr_advantage_proposal(osv.osv):

    _name = "hr.advantage.proposal"
    _description = "Proposition d augmentation des avantages"
    _columns = {
        'date':fields.date('Date'),
        'name': fields.many2one('account.period', 'Periode applicable', required=True),
        'start': fields.many2one('account.period', 'Periode effet'),
        'advantage_line':fields.one2many('hr.advantage.proposal.line', 'proposal_id', 'Nouvelle Grille'),
        }
    def validate (self, cr, uid, ids, context=None):
        """ Function doc """
        advantage_type_obj = self.pool.get('hr.employee.advantage.type')
        voiture_ids = advantage_type_obj.search(cr, uid, [('code', '=', 'T')])
        if voiture_ids != []:
            voiture_ids = voiture_ids[0]
        else:
            raise osv.except_osv(_('Warning'), _('le type avantages dont le code est "T" est introuvable'))
        advantage_obj = self.pool.get('hr.employee.advantage')
        advantage_line_obj = self.pool.get('hr.advantage.proposal.line')
        # rubrique_objt = self.pool.get('hr.payroll_ma.rubrique') #new line
        period_obj = self.pool.get('account.period')
        diff = 1

        for proposal in self.browse(cr, uid, ids):
            p_id = str(proposal.name.code).split('/')[1]
            ex_pid = '00/' + p_id
            pr_id = period_obj.search(cr, uid, [('code', 'like', p_id), ('code', 'not in', (ex_pid, str(proposal.name.code)))])
            period_id = proposal.name.id
            for line in proposal.advantage_line:
                for l in line:
                    employee_id = l.name.id
                    for type_adv in l.advantages_ids:
                        percentage = type_adv.perc_increase
                        adv_type = type_adv.name.id
                        adv_id = advantage_obj.search(cr, uid,
                            [('employee_id', '=', employee_id), ('state', '=', 'add'),
                            ('period_id', 'in', pr_id), ('name', '=', adv_type)])
                        amount_by_adv = 0
                        ad_browse = advantage_obj.browse(cr, uid, adv_id)
                        for a_id in ad_browse:
                            amount_by_adv += a_id.amount
                        perc_amount = amount_by_adv * percentage / 100
                        if adv_type == voiture_ids:
                            perc_amount = round(perc_amount, -3)
                        else:
                            perc_amount = round(perc_amount, -2)
                        # verification si cette info est deja la
                        verif_adv_id = advantage_obj.search(cr, uid,
                            [('employee_id', '=', employee_id), ('state', '=', 'add'),
                            ('period_id', '=', period_id), ('name', '=', adv_type)])

                        info = {'employee_id':employee_id,
                                'state':'add',
                                'period_id':period_id,
                                'name':adv_type,
                                'amount':perc_amount}

                        if len(verif_adv_id) == 0:
                            res = advantage_obj.create(cr, uid, info)
                        else:
                            res = advantage_obj.write(cr, uid, verif_adv_id, info)
                        # raise osv.except_osv(_('perc_amount'),_('amount_by_adv = %s \n perc_amount = %s')
                        #     %(amount_by_adv,perc_amount)) 
        return True
                
hr_advantage_proposal()

class hr_advantage_proposal_line(osv.osv):
    _name = "hr.advantage.proposal.line"
    _description = "Nouvelle Grille"
    
    def _get_perc(self, cr, uid, ids, name, arg, context={}):
        result = {}
        for payroll in self.browse(cr, uid, ids, context):
            net = 0
            if payroll.amount_initial == 0:
                if payroll.name.id:
                    raise osv.except_osv(_('Warning'),
                                        _('le salaire de base du matricule %s est egale a zero! \n Veuillez rectifier cela dans son contrat!') % (payroll.name.matricule))
                else:
                    raise osv.except_osv(_('Warning'), _('Veuillez supprimer cette ligne de proposition et regenerer SVP!'))
                    # return False
            else:
                result[payroll.id] = (payroll.amount_proposal - payroll.amount_initial) / payroll.amount_initial * 100
        return result
            
    _columns = {
        'name':fields.related('advantage_id', 'employee_id', type='many2one', relation='hr.employee', string='Employe'),
        'advantage_id':fields.many2one('hr.employee.advantage', 'Avantages'),  # ne sert juste qua recuperer les employees
        'advantages_ids':fields.one2many('adv.update.line', 'proposal_line_id', 'Ligne de proposition'),
        'proposal_id':fields.many2one('hr.advantage.proposal', 'Proposition'),
        # 'amount_initial':fields.related('advantage_id','amount',type='float',string='Montant Actuel'),
        # 'amount_proposal':fields.float('Montant propose'),
        # 'perc_increase':fields.function(_get_perc, method=True, type='float',digits=(16, 2), string='% Augmentation'),
        }
hr_advantage_proposal_line()

class adv_update_line(osv.TransientModel):
    """
        type avantages et Pourcentage d'augmentation
    """
    _name = "adv.update.line"
    _columns = {
        'proposal_line_id':fields.many2one('hr.advantage.proposal.line', 'Employe'),  # Ligne de proposition
        'name':fields.many2one('hr.employee.advantage.type', 'Type avantages'),
        'perc_increase': fields.float('Pourcentage augmentation', required=True),
        'amount_increase': fields.float('Montant augmentation', required=True),
        }
    _order = 'name'
adv_update_line()

class hr_advantage_mod_wiz(osv.TransientModel):
    _name = 'hr.advantage.mod.wiz'
    _description = 'Mis a jour des Avantages en masse'
    _columns = {
        'date': fields.date('Date', required=True),
        'start': fields.many2one('account.period', 'Date effet'),  # Rétro-actif depuis               
        'period_id': fields.many2one('account.period', 'Periode applicable', required=True, domain=[('date_start', '>', datetime.date.today().strftime('%Y-01-01'))]),
        'employee_ids': fields.many2many('hr.employee', 'adv_dept_emp_rel', 'sum_id', 'emp_id', 'Employee(s)', domain=[('active', '=', True)]),
        'advantage_ids':fields.one2many('advantage.line.wiz', 'adv_mod_id', 'Avantages'),
        # 'advantage_ids':fields.many2one('advantage.line.wiz','Avantages'),
        }

    def generate(self, cr, uid, ids, context=None):
        data = []
        data = self.read(cr, uid, ids, [])[0]
        # raise osv.except_osv(_('data'),_('data = %s')%(data))
        # contract_obj=self.pool.get('hr.contract')
        employee_obj = self.pool.get('hr.employee')
        advantage_obj = self.pool.get('hr.employee.advantage')
        period_obj = self.pool.get('account.period')
        proposal_obj = self.pool.get('hr.advantage.proposal')
        proposal_line_obj = self.pool.get('hr.advantage.proposal.line')
        period_id = data['period_id'][0]
        period_id = period_obj.browse(cr, uid, [period_id])[0]  # periode de paie et return an object type class
        start = period_obj.browse(cr, uid, [data['start'][0]])[0]  # periode pour les rappels
        # prev_period_id=period_obj.browse(cr,uid,[data['period_id'][0]-1])[0]
        adv_line_obj = self.pool.get('adv.update.line')
        # ############################################################
        date_today = datetime.date.today().strftime('%Y-%m-%d')
        created = []
        if not data['employee_ids']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Employee. And try again'))
        proposal = proposal_obj.search(cr, uid, [('name', '=', period_id.id)])  # return list of result
        if proposal == []:
            proposal = proposal_obj.create(cr, uid, {'name':period_id.id, 'start':start.id, 'date':date_today})
            # raise osv.except_osv(_('create'),_('create = %s')%(proposal))
        else:
            proposal = proposal[0]
            # raise osv.except_osv(_('update'),_('update = %s')%(proposal))
        created.append(proposal)  # "id du proposition salariale (list) identifier par la période"
        # raise osv.except_osv(_('created'),_('created = %s')%(created))
        # id des periode de l annee en cours
        p_id = data['period_id'][1].split('/')[1]
        ex_pid = '00/' + p_id
        pr_id = period_obj.search(cr, uid, [('code', 'like', p_id), ('code', '!=', ex_pid)])
        # raise osv.except_osv(_('period_id'),_('period_id = %s')%(pr_id))
        ################################################################################
        advtg_lines = self.pool.get('advantage.line.wiz').browse(cr, uid, data['advantage_ids'])
        # raise osv.except_osv(_('adv_lines'),_('advantage = %s')%(adv_lines))
        advantage_ids = []
        Erreur = []
        for employee_id in data['employee_ids']:
            related_adv = 0
            T = True
            for ad_lines in advtg_lines:
                adv_id = advantage_obj.search(cr, uid,
                    [('employee_id', '=', employee_id), ('state', '=', 'add'),
                    ('period_id', 'in', pr_id), ('name', '=', ad_lines.name.id)]) 
                
                if len(adv_id) != 0:
                    if T:
                        related_adv = adv_id[0]
                        T = False
                    # amount_by_adv = 0
                    # ad_obj = advantage_obj.browse(cr,uid,adv_id)
                    # for a_id in ad_obj:
                    #     amount_by_adv += a_id.amount
                    # raise osv.except_osv(_('amount_by_adv'),_('amount_by_adv = %s')%(amount_by_adv))

                    # advantage_ids.append(adv_id[0])
                    proposal_line = proposal_line_obj.search(cr, uid,
                        [('proposal_id', '=', created[0]), ('advantage_id', '=', related_adv)])
                    if len(proposal_line) == 0:
                        pl = proposal_line_obj.create(cr, uid,
                                {'advantage_id':adv_id[0], 'proposal_id':created[0]})
                        # adv_lines=self.pool.get('advantage.line.wiz').browse(cr,uid,data['advantage_ids'])
                        advantage = {'proposal_line_id':pl,
                            'name':ad_lines.name.id,
                            'perc_increase': ad_lines.perc_increase,
                            'amount_increase': ad_lines.amount_increase,
                            }
                        adv_line_obj.create(cr, uid, advantage)

                    else:
                        advantage = {'proposal_line_id':proposal_line[0],
                            'name':ad_lines.name.id,
                            'perc_increase': ad_lines.perc_increase,
                            'amount_increase': ad_lines.amount_increase,
                            }
                        adv_line_obj.create(cr, uid, advantage)

        # return True

        return {
            'domain': "[('id','in', [" + ','.join(map(str, created)) + "])]",
            'name': 'Avantages',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.advantage.proposal',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }
        
    def _from_date(self, cursor, user, context={}):
        return datetime.date.today().strftime('%Y-%m-%d');


    _defaults = {
        'date': _from_date, }
hr_advantage_mod_wiz()

class advantage_line_wiz(osv.TransientModel):

    _name = "advantage.line.wiz"
    _columns = {
        'adv_mod_id':fields.many2one('hr.advantage.mod.wiz', 'Avantages'),
        'name':fields.many2one('hr.employee.advantage.type', 'Type Avantages'),
        'perc_increase': fields.float('Pourcentage augmentation', required=True),
        'amount_increase': fields.float('Montant augmentation', required=True),
        }
    
advantage_line_wiz()


class hr_advantage_proposal_validate(osv.TransientModel):
    _name = "hr.advantage.proposal.validate"
    _description = "Validation Proposition avantages"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):

        if context is None:
            context = {}
        res = super(hr_advantage_proposal_validate, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        return res

    def validate_proposal(self, cr, uid, ids, context=None):

        adv_obj = self.pool.get('adv.update.line')
        prop_obj = self.pool.get('hr.advantage.proposal')
        prop_line_obj = self.pool.get('hr.advantage.proposal.line')
        
        
        active_ids = context['active_ids']
        props = []
        prop_line = adv_obj.read(cr, uid, active_ids, ['proposal_line_id'])
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
        # planning_obj = self.pool.get('hr.employee.overtime')
        # planning_obj.write(cr,uid,context['active_ids'],{'state':'refuse'})
        return {}
hr_advantage_proposal_validate()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
