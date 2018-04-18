# -*- coding: utf-8 -*-
from openerp import api,  exceptions,  fields,  models,  _


class hrPlanElearning(models.Model):
    _name = 'hr.plan.elearning'

    name = fields.Char(string=u'Libellé', size=64, required=False, readonly=False)
    module_id = fields.Many2one('hr.employee.formation.module', string='Module')
    date_start = fields.Date(string=u'Prévision début')
    date_end= fields.Date(string=u'Prévision fin')
    intervenant = fields.Char(string='Intervenant', size=64, required=False, readonly=False)
    total_besoin = fields.Integer(string=u'Besoin exprimé')
    budget_euro = fields.Float(string='Budget en Euros', digits=(6, 2))
    budget_ariary = fields.Float(string='Budget en Ariary', digits=(6, 2))
    besoin_accorde = fields.Integer(string=u'Besoin accordé')
    beneficiaire = fields.Integer(string=u'Bénéficiaire')
    cout = fields.Float(string=u'Coût total', digits=(6, 2))
    taken_seats = fields.Float(string='Taux', digits=(4, 2), compute="_taken_seats_4")
    branche = fields.Char(string='Branche', size=64, required=False, readonly=False)
    objectif_id = fields.Many2one('hr.formation.objectif', string='Objectif')
    #session_elearning_ids = fields.Many2many('hrSessionElearning', string='Session e-learning')
    session_elearning_2_ids = fields.One2many('hr.session.elearning', 'plan_formation_id', string=u'Session e-learning')

    # compute fields
    @api.depends ('beneficiaire', 'besoin_accorde')
    def _taken_seats_4(self):
        for r in self:
            if not r.besoin_accorde:
                r.taken_seats=0.0
            else:
                r.taken_seats=100 * r.beneficiaire/r.besoin_accorde

    # compute fields
    @api.multi
    def name_get(self):
        result = super(hrPlanElearning,  self).name_get()
        res = []
        print("result = %s" % result)
        for rec in result:
            # rec = (rec.id,  r_name)
            el_obj = self.browse(rec[0])
            r_name = rec[1] + ' '+ '[' + el_obj.objectif_id.name + '] ' +' ' + '[' + el_obj.module_id.name + '] '
            res.append((el_obj.id,  r_name))
        return res
        """
        for record in self:
            r_name=record.name
            if record.intervenant:
                r_name = '[' + record.intervenant + '] ' + r_name
            result.append((record.id,  r_name))
        return result
        """
