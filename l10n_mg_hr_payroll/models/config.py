# -*- coding: utf-8 -*-

from openerp.osv import osv, fields


class hr_payroll_ma_parametres(osv.osv):
    _name = 'hr.payroll_ma.parametres'
    _description = 'Parametres'

    def _get_credit_account(self, cr, uid, context):
        account_obj = self.pool.get('account.account')
        res = account_obj.search(cr, uid, [('code', '=', '4432')], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_debit_account(self, cr, uid, context):
        account_obj = self.pool.get('account.account')
        res = account_obj.search(cr, uid, [('code', '=', '6171')], limit=1)
        if res:
            return res[0]
        else:
            return False

    def _get_ir_account(self, cr, uid, context):
        account_obj = self.pool.get('account.account')
        res = account_obj.search(cr, uid, [('code', '=', '44525')], limit=1)
        if res:
            return res[0]
        else:
            return False

    _columns = {
        'smig': fields.float('SMIG'),
        'charge': fields.float('Charges de familles',
                               help='Les charges de famille deduites de IGR'),
        'fraispro': fields.float('Frais Proffessionnels'),
        'plafond': fields.float('Plafond'),
        'credit_account_id': fields.many2one('account.account',
                                             'Compte de credit IGR'),
        'partner_id': fields.many2one('res.partner', 'Partenaire',
                                      change_default=True, readonly=True),
        'salary_credit_account_id': fields.many2one('account.account',
                                                    'Compte de credit'),
        'roundoff_account_id': fields.many2one('account.account',
                                               u'Compte d\'arrondi'),
        'salary_debit_account_id': fields.many2one('account.account',
                                                   u'Compte de debit'),
        'analytic_account_id': fields.many2one('account.analytic.account',
                                               'Analytic Account'),
        'index': fields.float('Point Indice', digits=(12, 9)),
        'seniority_override': fields.boolean('Anciennete sur formule'),
        'salary_on_index': fields.boolean('Calcul salaire sur indice'),
        'debut_pointage': fields.char('Debut pointage', size=2),
        'fin_pointage': fields.char('Fin pointage', size=2),
        'rubrique_ids': fields.one2many('hr.payroll_ma.ligne_rubrique',
                                        'parameter_id', 'Les rubriques'),
                 }
    _defaults = {
        # 'smig': lambda *a: 10,
        # 'charge': lambda *a: 15,
        # 'fraisPro': lambda *a: 0.17,
        # 'plafond': lambda *a: 2000,
        'salary_credit_account_id': _get_credit_account,
        'salary_debit_account_id': _get_debit_account,
        'credit_account_id': _get_ir_account,
    }


hr_payroll_ma_parametres()


class hr_ir(osv.osv):
    _name = 'hr.payroll_ma.ir'
    _description = 'IR'
    _columns = {
        'debuttranche': fields.float('Debut de Tranche'),
        'fintranche': fields.float('Fin de tranche'),
        'taux': fields.float('Taux'),
        'somme': fields.float('Somme a deduire')
    }


hr_ir()


class hr_anciennete(osv.osv):
    _name = 'hr.payroll_ma.anciennete'
    _description = 'Configurer les tranches de la prime d\'anciennete'
    _columns = {
        'debuttranche': fields.float('Debut Tranche'),
        'fintranche': fields.float('Fin Tranche'),
        'taux': fields.float('Taux')
        # 'partner_id': fields.many2one(
        # 'res.partner', 'Partenaire', change_default=True,
        # readonly=True, required=True, ),
            }


hr_anciennete()


class hr_cotisation(osv.osv):

    _name = 'hr.payroll_ma.cotisation'
    _description = 'Configurer les cotisations'
    _columns = {
        'code': fields.char("Code", size=64),
        'name': fields.char("Designation", size=64),
        'tauxsalarial': fields.float("Taux Salarial"),
        'tauxpatronal': fields.float("Taux Patronal"),
        'plafonee': fields.boolean('Cotisation plafonee'),
        'ir': fields.boolean('Soumis a IR'),
        'plafond': fields.float('Plafond'),
        'plafond_tri': fields.boolean('Plafond Trimestre'),
        'credit_account_id': fields.many2one('account.account',
                                             'Compte de credit'),
        'debit_account_id': fields.many2one(
            'account.account', 'Compte de debit',
            help='Le compte de debit pour la part paronale'),
        'rubriques': fields.char('Rubriques', size=128),
    }
    _order = 'code'


hr_cotisation()


class hr_cotisation_type(osv.osv):

    _name = 'hr.payroll_ma.cotisation.type'
    _description = 'Configurer les types de cotisation'
    _columns = {
        'name': fields.char("Designation", size=64),
        'cotisation_ids': fields.many2many(
            'hr.payroll_ma.cotisation', 'salary_cotisation',
            'cotisation_id', 'cotisation_type_id', 'Cotisations'),
    }


hr_cotisation_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
