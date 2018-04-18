# -*- coding: utf-8 -*-

from openerp import api,  exceptions,  fields,  models,  _


class hrPlanFormationVersion3(models.Model):
    _name = 'hr.plan.formation.version_3'

    name = fields.Char(string=u'Libellé')
    objectif_id = fields.Many2one('hr.formation.objectif', string='Objectif', required=True)
    branche_id = fields.Many2one('hr.employee.branche', string='Branche', required=True)
    module_id = fields.Many2one('hr.employee.formation.module', string='Module', required=True)
    date_start = fields.Date(string=u'Prévision début')
    date_end= fields.Date(string=u'Prévision fin')
    intervenant = fields.Char(string='Intervenant')
    total_besoin = fields.Integer(string=u'Besoin exprimé')
    budget_euro = fields.Float(string='Budget en Euros', digits=(6, 2))
    budget_ariary = fields.Float(string='Budget en Ariary', digits=(6, 2))
    besoin_accorde = fields.Integer(string=u'Besoin accordé')
    beneficiaire = fields.Integer(string=u'Bénéficiaire')
    taken_seats=fields.Float( string='Taux', digits=(4, 2), compute="_taken_seats_2")
    cout = fields.Float(string=u'Coût total', digits=(6, 2))
    test_besoin = fields.Char(string='Besoin Test')
    session_plan_ids = fields.One2many('hr.session.plan.version_3', 'plan_formation_id', string='session')
    observations = fields.Text(string='Observations')

    # compute field
    @api.depends ('beneficiaire', 'besoin_accorde')
    def _taken_seats_2(self):
        for r in self:
            if not r.besoin_accorde:
                r.taken_seats=0.0
            else:
                r.taken_seats=100 * r.beneficiaire/r.besoin_accorde

    @api.multi
    def name_get(self):
        result = super(hrPlanFormationVersion3,  self).name_get()
        res = []
        print("result = %s" % result)
        for rec in result:
            # rec = (rec.id,  r_name)
            el_obj = self.browse(rec[0])
            r_name = rec[1] + ' '+ '[' + el_obj.objectif_id.name + '] ' +' ' + '[' + el_obj.branche_id.name + '] '+''+'[' + el_obj.module_id.name + ']'
            res.append((el_obj.id,  r_name))
        return res
