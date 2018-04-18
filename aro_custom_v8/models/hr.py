# coding:UTF-8
"""
.. module:: hr
   :platform: Unix, Windows
   :synopsis: Module pour les rajout aux modules de la RH.

.. moduleauthor:: Geerish Sumbojee <geerish@omerp.net>


"""
#import logging

#from openerp import addons
#from openerp import tools
from openerp.osv import fields, osv
from openerp.tools.translate import _


class hr_employee_advantage_type(osv.osv):
    """Définition des type d´avantages

    Le taux sera utilisé pour calculer le montant a déduire

    """
    _name = 'hr.employee.advantage.type'
    _columns = {
        'name':fields.char('Description'),
        'rate':fields.float('Taux'),
        'code':fields.char('Code'),
    }
hr_employee_advantage_type()

class hr_employee_advantage(osv.osv):
    _name = 'hr.employee.advantage'
    _columns = {
        'period_id': fields.many2one('account.period', 'Periode'),
        'employee_id': fields.many2one('hr.employee', 'Employe'),
        'name':fields.many2one('hr.employee.advantage.type', 'Advantage'),
        'amount':fields.float('Montant'),
        'state': fields.selection((('add', 'Attribuer'), ('remove', 'Consommer'), ('cancel', 'Annuler')), 'Action'),
        'ref': fields.char('Reference', size=16),
    }


    def write(self, cr, uid, ids, vals, context=None):
        if 'state' in vals:
            if vals['state'] != 'add':
                if vals['amount'] > 0:
                    vals['amount'] = vals['amount'] * -1
        res = super(hr_employee_advantage, self).write(cr, uid, ids, vals, context=context)
        return res

    def create(self, cr, uid, vals, context=None):
        if 'state' in vals:
            if vals['state'] != 'add':
                if vals['amount'] > 0:
                    vals['amount'] = vals['amount'] * -1
        res = super(hr_employee_advantage, self).create(cr, uid, vals, context=context)
        return res


hr_employee_advantage()

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _description = "Ajout de champ spécifique à la fiche employé"

    #function to get groupe
    def _get_group(self, cr, uid, ids, field_name, args, context):
        res={}
        for employee in self.browse(cr,uid,ids):
            res[employee.id]=False
            for categ in employee.category_ids:
                res[employee.id]=categ.parent_id.id
        return res

    #new function to find employee in a group #
    def _search_group_employee(self, cr, uid, obj, field_name, args, context=None):
        res_buff = []
        arg = str(args[0][2])
        critere_arg = [('name','ilike',arg)]
        res = []
        obj_employee_category = self.pool.get('hr.employee.category')

        ids = obj.search(cr,uid,[]) # ids of employee
        res = self._get_group(cr, uid, ids, field_name, args, context)
        groupe_ids = obj_employee_category.search(cr,uid,critere_arg)
        if len(groupe_ids)!=0:
            groupe_id = groupe_ids[0]
            for k,v in res.items():
                if groupe_id == v:
                    res_buff.append(k)
                else:
                    print("nothing to show") # just for debugging
            if len(res_buff)!=0:
                res = []
                res = res_buff
            else:
                raise osv.except_osv(_('Desole'), _('Pas d\'employee dans ce groupe '))
        else:
            raise osv.except_osv(_('Error'), _('Ce groupe n\'existe pas'))
        return [('id','in',res)]

    _description = "Ajout de champ spécifique à la fiche employé"

    #function to get groupe
    def _get_group(self, cr, uid, ids, field_name, args, context):
        res={}
        for employee in self.browse(cr,uid,ids):
            res[employee.id]=False
            for categ in employee.category_ids:
                res[employee.id]=categ.parent_id.id
        return res

    #new function
    def _search_group_employee(self, cr, uid, obj, field_name, args, context=None):
        res_buff = []
        arg = str(args[0][2])
        critere_arg = [('name','ilike',arg)]
        res = []
        obj_employee_category = self.pool.get('hr.employee.category')

        ids = obj.search(cr,uid,[]) # ids of employee
        res = self._get_group(cr, uid, ids, field_name, args, context)
        groupe_ids = obj_employee_category.search(cr,uid,critere_arg)
        if len(groupe_ids)!=0:
            groupe_id = groupe_ids[0]
            for k,v in res.items():
                if groupe_id == v:
                    res_buff.append(k)
                else:
                    print("nothing to show") # just for debugging
            if len(res_buff)!=0:
                res = []
                res = res_buff
            else:
                raise osv.except_osv(_('Desole'), _('Pas d\'employee dans ce groupe '))
        else:
            raise osv.except_osv(_('Error'), _('Ce groupe n\'existe pas'))
        return [('id','in',res)]

    _columns = {
        'situation': fields.selection((('ret', 'Retraite'), ('lic', 'Licencie'), ('dec', 'Decede'), ('dem', 'Demissionaire'), ('dis', 'En disponibilite'), ('en_poste', 'En Poste')), 'Etat contractuel'),
        'employee_advantage_ids':fields.one2many('hr.employee.advantage', 'employee_id', 'Avantages'),
        'date_bis':fields.date('Embauche2'),
        'codepaie':fields.char('Mode Payement', size=8),
        'groupe_catg':fields.char('Categorie de Groupe', size=32),
        #'groupe_related': fields.related('category_ids','groupe_related',type='many2one', relation='hr.employee', string='groupe', store=False, readonly=False)
        'groupe' : fields.function(_get_group,fnct_search=_search_group_employee,type='many2one', relation='hr.employee.category',string='Groupe', method=True, readonly=False)
    }
    _defaults = {
        #'state': 'en_poste',
    }
hr_employee()

class hr_holidays(osv.osv):
    _inherit = "hr.holidays"
    _columns = {
    'replacement_id': fields.many2one('hr.employee', 'Interim'),
    'place':fields.char('Lieu de jouissance', size=64),
    'dap':fields.many2one('res.users', 'DAP'),
    'dfp':fields.many2one('res.users', 'DFP'),
    }

    def dap_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'dap':uid})

    def dfp_validate(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'dfp':uid})

hr_holidays()

class hr_department(osv.osv):
    _inherit = 'hr.department'
    _columns = {
        'code_ser':fields.char('code service', size=32),
    'niveau':fields.char('niveau', size=2),
    'code_parent':fields.char('code parent', size=32)
    }
hr_department()

class hr_contract_type(osv.osv):
    _inherit = 'hr.contract.type'
    _columns = {
    'code':fields.char('code parent', size=32)
    }
hr_contract_type()

class hr_employee_category(osv.osv):
    _inherit = 'hr.employee.category'
    _columns = {
        'code_catg':fields.char('code categorie', size=32),
        'reference_catg':fields.char('reference categorie', size=32)
    }
hr_employee_category()

