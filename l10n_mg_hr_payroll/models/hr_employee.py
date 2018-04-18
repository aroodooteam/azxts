# -*- coding: utf-8 -*-

# from openerp import netsvc
from openerp.osv import fields, osv
# import openerp.pooler
# from openerp.tools.translate import _
import time
import logging
logger = logging.getLogger(__name__)


class payment_mode(osv.osv):

    _name = "payment.mode"
    _description = "Mode de payement"

    _columns = {
        'code': fields.char('Code', size=8),
        'name': fields.char('Type', size=64),
        'ref': fields.char('Reference', size=64),
        }


payment_mode()


class payment_term(osv.osv):

    _name = "payment.term"
    _description = "Mode de Reglement"

    def _get_default_rate(self, cr, uid, arg, context=None):
        terms = self.search(cr, uid,
                            [('employee_id', '=', context['employee_id'])],
                            context=None)
        terms = self.browse(cr, uid, terms, context=None)
        rate = 100
        for term in terms:
            rate = rate - term.rate
        return rate

    _columns = {
        # 'name':fields.selection(
        # [('virement', 'Virement'), ('cheque', 'Cheque'),
        # ('espece', 'Espece'), ], 'Mode De Reglement'),
        'name': fields.many2one('payment.mode', 'Mode De Reglement'),
        'employee_id': fields.many2one('hr.employee', 'Employe'),
        'bank_account_id': fields.many2one('res.partner.bank', 'RIB'),
        'bank_id': fields.related('bank_account_id', 'bank',
                                  relation='res.bank', type='many2one',
                                  string='Banque', readonly=True),
        # 'bank_account_number':fields.char('Numero de compte', size=64),
        'amount': fields.float('Montant'),  # il faut mettre une contrainte
        # pour empecher l'utilisteur de mettre total de taux > 100%
        'rate': fields.float('Taux'),  # rate a ete changer en montant donc
        # faut modifier la contrainte de taux = 100%
        'state': fields.selection(
            (('open', 'Actif'), ('cancel', 'Inactif')),
            'Etat'),
        }
    _defaults = {
        'state': 'open',
        # 'rate': lambda self, cr, uid,
        # context: self._get_default_rate(cr,uid,fields,context=context),
        }


payment_term()


class hr_employee(osv.osv):
    _inherit = 'hr.employee'

    def _get_latest_contract(self, cr, uid, ids, field_name,
                             args, context=None):
        res = {}
        obj_contract = self.pool.get('hr.contract')
        for emp in self.browse(cr, uid, ids, context=context):
            contract_ids = obj_contract.search(
                cr, uid, [('employee_id', '=', emp.id)],
                order='date_start', context=context)
            if contract_ids:
                res[emp.id] = contract_ids[-1:][0]
            else:
                res[emp.id] = False
        return res

    def _get_visibility(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        for emp in self.browse(cr, uid, ids, context=context):
            visible = False
            if emp.user_id.id == uid:
                visible = True
            elif emp.parent_id.user_id.id == uid:
                visible = True
            else:
                group_ids = self.pool.get('res.users').browse(
                    cr, uid, uid, context=context).groups_id
                group_user_id = self.pool.get("ir.model.data").get_object_reference(cr, uid, 'base', 'group_hr_user')[1]
                if group_user_id in [group.id for group in group_ids]:
                    visible = True
                else:
                    group_user_id = self.pool.get("ir.model.data").get_object_reference(cr, uid, 'base', 'group_hr_manager')[1]
                    if group_user_id in [group.id for group in group_ids]:
                        visible = True
            res[emp.id] = visible
        return res

    def _get_children(self, cr, uid, ids, field_name, arg, context):
        employees = self.browse(cr, uid, ids)
        res = {}
        for employee in employees:
            count = 0
            for child in employee.children_ids:
                count += 1
            res[employee.id] = count
        return res

    def _get_chargefam(self, cr, uid, ids, field_name, arg, context):
        employees = self.browse(cr, uid, ids)
        res = {}
        for employee in employees:
            count = 0
            for child in employee.children_ids:
                ages = child.age.split()
                if len(ages) > 1:
                    if int(ages[0][:-1]) < 21:
                        count += 1
            res[employee.id] = count
        return res

    def _get_date_start(self, cr, uid, ids, field_name, arg, context):
        employees = self.browse(cr, uid, ids)
        res = {}
        for employee in employees:
            if not employee.contract_ids:
                res[employee.id] = '1900-01-01'
                continue
            for contract in employee.contract_ids:
                res[employee.id] = contract.date_start
                break
        return res

    def name_get(self, cr, uid, ids, context=None):
        # if not len(ids):
        #    return []
        res = []
        for employee in self.browse(cr, uid, ids, context=context):
            p_name = employee.name
            if employee.matricule:
                p_name = '[' + employee.matricule + '] ' + p_name
            res.append((employee.id, p_name))
        return res

    def _get_is_birthday(self, cr, uid, ids, field_name, args, context=None):
        res = {}
        this_week = time.strftime('%W')
        for emp in self.browse(cr, uid, ids):
            if not emp.birthday:
                res[emp.id] = False
            elif time.strftime('%W', time.strptime(emp.birthday, '%Y-%m-%d')) == this_week:
                res[emp.id] = True
            else:
                res[emp.id] = False
        return res

    def _search_is_birthday(self, cr, uid, obj, name, args,
                            domain=None, context=None):
        res = []
        ids = self.search(cr, uid, [('active', '=', True)])
        for emp in self.browse(cr, uid, ids):
            for flds, operator, value in args:
                if not value and not emp.is_birthday:
                    res.append(emp.id)
                if value and emp.is_birthday:
                    res.append(emp.id)
        return [('id', 'in', res)]

    _columns = {
        'visible': fields.function(_get_visibility, method=True,
                                   string='Visible', type='boolean'),
        'matricule': fields.char('Matricule', size=64),
        'cin': fields.char('CIN', size=64),
        'date': fields.function(_get_date_start, method=True,
                                string='Date Embauche', type='date'),
        # 'date': fields.date(
        # 'Date entree',
        # help='''Cette date est requipe pour le
        # calcule de la prime d' anciennete'''),
        'anciennete': fields.boolean(
            'Prime anciennete',
            help='Est ce que cet employe benificie de la prime d\'anciennete'),
        'mode_reglement': fields.selection(
            [('virement', 'Virement'), ('cheque', 'Cheque'),
             ('espece', 'Espece')], 'Mode De Reglement'),
        'payment_term_id': fields.one2many('payment.term', 'employee_id',
                                           'Mode de Paiement'),
        'bank': fields.char('Banque', size=128),
        'compte': fields.char('Compte bancaire', size=128),
        # 'chargefam' : fields.integer('Nombre de personnes a charge'),
        'chargefam': fields.function(_get_chargefam, method=True,
                                     type='float'),
        'logement': fields.float('Abattement Fr Logement'),
        'affilie': fields.boolean(
            'Affilie',
            help='Est ce qu on va calculer les cotisations pour cet employe'),
        'address_home': fields.char('Adresse Personnelle', size=128),
        'address': fields.char('Adresse Professionnelle', size=128),
        'phone_home': fields.char('Telephone Personnel', size=128),
        'licexpiry': fields.char('Lic Expiry', size=128),
        'licenseno': fields.char('Lic No', size=128),
        'licensetyp': fields.char('Lic Type', size=128),
        'manager': fields.boolean('Is a Manager'),
        'medic_exam': fields.date('Medical Examination Date'),
        'place_of_birth': fields.char('Place of Birth', size=30),
        'cin_date': fields.date('Date CIN'),
        'cin_place': fields.char('Lieu CIN', size=30),
        # 'children': fields.integer('Number of Children'),
        'children': fields.function(_get_children, method=True, type='float'),
        'vehicle': fields.char('Company Vehicle', size=64),
        'vehicle_distance': fields.integer('Home-Work Distance',
                                           help="In kilometers"),
        'contract_ids': fields.one2many('hr.contract', 'employee_id',
                                        'Contracts'),
        'contract_id': fields.function(_get_latest_contract, method=True,
                                       string='Contract', type='many2one',
                                       relation="hr.contract",
                                       help='Latest contract of the employee'),
        'contract_type_id': fields.related('contract_id', 'type_id',
                                           string='Contrat', type='many2one',
                                           relation='hr.contract.type',
                                           readonly=1),
        'aptitude_job': fields.float(u'Aptitude/Poste'),
        'qualification_job': fields.float('Qualification/Poste'),
        'training_job': fields.float('Formation/Poste'),
        'is_birthday': fields.function(_get_is_birthday, method=True,
                                       type='boolean',
                                       fnct_search=_search_is_birthday),
    }
    _defaults = {
        # 'chargefam' : lambda * a: 0,
        'logement': lambda * a: 0,
        'anciennete': lambda * a: 'True',
        'affilie': lambda * a: 'True',
        'date': lambda * a: time.strftime('%Y-%m-%d'),
        'mode_reglement': lambda * a: 'virement'
    }

    def name_search(self, cr, user, name, args=None, operator='ilike',
                    context=None, limit=80):
        """Search by bank code in addition to the standard search"""
        results = super(hr_employee, self).name_search(
            cr, user, name, args=args, operator=operator,
            context=context, limit=limit)
        ids = self.search(cr, user, [('matricule', operator, name)],
                          limit=limit, context=context)
        # Merge the results
        results = list(set(results + self.name_get(cr, user, ids, context)))
        return results

    def name_search2(self, cr, user, name='', args=None, operator='ilike',
                     context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}
        ids = []
        if name:
            ids = self.search(cr, user, [('matricule', '=', name)] + args,
                              limit=limit, context=context)
        if not ids:
            ids = self.search(cr, user, [('name', operator, name)] + args,
                              limit=limit, context=context)
        return self.name_get(cr, user, ids, context=context)


hr_employee()

# Contract wage type period name


class hr_contract_wage_type_period(osv.osv):
    _name = 'hr.contract.wage.type.period'
    _description = 'Wage Period'
    _columns = {
        'name': fields.char('Period Name', size=50,
                            required=True, select=True),
        'factor_days': fields.float('Hours in the period',
                                    digits=(12, 4), required=True,)
    }
    _defaults = {
        'factor_days': 173.33
    }


hr_contract_wage_type_period()


class hr_contract_wage_type(osv.osv):
    _name = 'hr.contract.wage.type'
    _description = 'Wage Type'
    _columns = {
        'name': fields.char('Wage Type Name', size=50,
                            required=True, select=True),
        'period_id': fields.many2one('hr.contract.wage.type.period',
                                     'Wage Period', required=True),
        'type': fields.selection(
            [('gross', 'Gross'), ('net', 'Net')], 'Type', required=True),
        'factor_type': fields.float('Factor for hour cost',
                                    digits=(12, 4), required=True,)}
    _defaults = {
        'type': 'gross',
        'factor_type': 1.8
    }


hr_contract_wage_type()


class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _description = 'Contract Type'
    _columns = {
        'name': fields.char('Contract Type', size=32, required=True),
    }


hr_contract_type()


class hr_contract(osv.osv):
    _inherit = 'hr.contract'
    _description = 'Employee Contract'

    _columns = {
        'name': fields.char('Contract Reference', size=32, required=True),
        'employee_id': fields.many2one('hr.employee', 'Employee',
                                       required=True),
        'department_id': fields.related('employee_id', 'department_id',
                                        type='many2one',
                                        relation='hr.department',
                                        string='Department',
                                        readonly=True),
        'type_id': fields.many2one('hr.contract.type', 'Contract Type',
                                   required=True),
        'job_id': fields.many2one('hr.job', 'Job Title'),
        'date_start': fields.date('Start Date', required=True),
        'date_end': fields.date('End Date'),
        'trial_date_start': fields.date('Trial Start Date'),
        'trial_date_end': fields.date('Trial End Date'),
        'working_hours': fields.many2one('resource.calendar',
                                         'Working Schedule'),
        'wage_type_id': fields.many2one('hr.contract.wage.type',
                                        'Wage Type', required=False),
        'wage': fields.float('Wage', digits=(16, 2), required=True),
        'advantages': fields.text('Advantages'),
        'advantages_net': fields.float('Net Advantages Value', digits=(16, 2)),
        'advantages_gross': fields.float('Gross Advantages Value',
                                         digits=(16, 2)),
        'notes': fields.text('Notes'),
        'salary_clause': fields.char('Clause specifique pour le salaire',
                                     size=64),
        'working_days_per_month': fields.integer('jours travailles par mois'),
        'hour_salary': fields.float('salaire Heure'),
        'monthly_hour_number': fields.float('Nombre Heures par mois'),
        # 'cotisation': fields.many2one('hr.payroll_ma.cotisation.type',
        # 'Type cotisations', required=True),
        # 'rubrique_ids': fields.one2many('hr.payroll_ma.ligne_rubrique',
        # 'id_contract', 'Les rubriques'),
        'assiduite': fields.boolean('Assuidite')
    }
    _defaults = {
        'working_days_per_month': lambda * a: 26,

    }

    # function used for hr_payroll
    """
    def net_to_brute(self, cr, uid, ids, context={}):
        id_contract = ids[0]
        contract = self.pool.get('hr.contract').browse(cr, uid, id_contract)
        salaire_base = contract.wage
        cotisation = contract.cotisation
        personnes = contract.employee_id.chargefam
        params = self.pool.get('hr.payroll_ma.parametres')
        objet_ir = self.pool.get('hr.payroll_ma.ir')
        id_ir = objet_ir.search(cr, uid, [])
        liste = objet_ir.read(cr, uid, id_ir,
                              ['debuttranche', 'fintranche', 'taux', 'somme'])
        ids_params = params.search(cr, uid, [])
        dictionnaire = params.read(cr, uid, ids_params[0])
        abattement = personnes * dictionnaire['charge']
        base = 0
        salaire_brute = salaire_base
        trouve = False
        trouve2 = False
        while(trouve is False):
            salaire_net_imposable = 0
            cotisations_employee = 0
            for cot in cotisation.cotisation_ids:
                if cot.plafonee and salaire_brute >= cot.plafond:
                    base = cot.plafond
                else:
                    base = salaire_brute
                cotisations_employee += base * cot['tauxsalarial'] / 100
            fraispro = salaire_brute * dictionnaire['fraispro'] / 100
            if fraispro < dictionnaire['plafond']:
                salaire_net_imposable = salaire_brute - fraispro
                salaire_net_imposable -= cotisations_employee
            else:
                salaire_net_imposable = salaire_brute - dictionnaire['plafond']
                salaire_net_imposable -= cotisations_employee
            for tranche in liste:
                if (salaire_net_imposable >= tranche['debuttranche']/12) \
                   and (salaire_net_imposable < tranche['fintranche']/12):
                    taux = (tranche['taux'])
                    somme = (tranche['somme']/12)
            ir = (salaire_net_imposable - (somme*12))*taux/100 - abattement
            if (ir < 0):
                ir = 0
            salaire_net = salaire_brute - cotisations_employee - ir
            if (int(salaire_net) == int(salaire_base) and not trouve2):
                trouve2 = True
                salaire_brute -= 1
            if (round(salaire_net, 2) == salaire_base):
                trouve = True
            elif not trouve2:
                salaire_brute += 0.5
            elif trouve2:
                salaire_brute += 0.01

        self.write(cr, uid, [contract.id], {'wage': round(salaire_brute, 2)})
        return True
    """


hr_contract()


class hr_holidays_status(osv.osv):
    _inherit = "hr.holidays.status"
    _description = 'Holidays'
    _columns = {
        'payed': fields.boolean('paye', required=False),
    }
    _defaults = {
        'payed': lambda * args: True
    }


hr_holidays_status()
