# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrSessionFormationVersion2(models.Model):
    _name = 'hr.session.formation.version_2'

    plan_formation_id = fields.Many2one('hr.plan.formation.version_2', string=u'Libellé')
    objectif_id = fields.Many2one('hr.formation.objectif', string='Objectif')
    branche_id = fields.Many2one('hr.employee.branche', string='Branche')
    name= fields.Many2one('hr.employee.formation.module', string='Module')
    date_start = fields.Date(string=u'Prévision début')
    date_end= fields.Date(string=u'Prévision fin')
    intervenant = fields.Char(string='Intervenant')
    total_besoin = fields.Integer(string=u'Besoin exprimé')
    budget_euro = fields.Float(string='Budget en Euros', digits=(6,2))
    budget_ariary = fields.Float(string='Budget en Ariary', digits=(6,2))
    besoin_accorde = fields.Integer(string=u'Besoin accordé')
    beneficiaire = fields.Integer(string=u'Bénéficiaire')
    taken_seats=fields.Float( string='Taux', digits=(4,2), compute="_taken_seats")
    cout = fields.Float(string='Coût total', digits=(6,2))
    formation_participant_ids = fields.One2many('hr.formation.participant', 'session_formation_id', string='Participants')
    date_session = fields.Date(string='Date effective')
    employee_id = fields.Many2one('hr.employee', string=u'Employé')
    attendee_ids = fields.Many2many('hr.employee', string='Attendee')
    #name = fields.Char(string='',size=64,required=False, readonly=False,defaults={:False})

    # compute field
    @api.depends ('beneficiaire','besoin_accorde')
    def _taken_seats(self):
        for r in self:
            if not r.besoin_accorde:
                r.taken_seats=0.0
            else:
                r.taken_seats=100 * r.beneficiaire/r.besoin_accorde
