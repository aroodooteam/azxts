# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrSessionPlanVersion3(models.Model):
    _name = 'hr.session.plan.version_3'

    plan_formation_id = fields.Many2one('hr.plan.formation.version_3', string=u'Année')
    objectif_id = fields.Many2one('hr.formation.objectif',string='Objectif')
    branche_id = fields.Many2one('hr.employee.branche',string='Branche')
    module_id= fields.Many2one('hr.employee.formation.module',string='Module')
    date_session = fields.Date(string=u'Date Début')
    session_place = fields.Char(string='Lieu')
    instructor_id = fields.Many2one('hr.formation.instructor',string='Animateur')
    session_plan_ids = fields.Many2many('hr.plan.formation.version_3',string='Session')
    attendee_ids = fields.Many2many('hr.employee',string='Attendee')
    plan_formation_objectif_id = fields.Char(related='plan_formation_id.objectif_id.name', readonly=True, string='Objectif')
    plan_formation_branche_id = fields.Char(related='plan_formation_id.branche_id.name', readonly=True,string='Branche')
    plan_formation_module_id = fields.Char(related='plan_formation_id.module_id.name', readonly=True,string='Module')
    date_fin_session = fields.Date(string='Date Fin')
    cout_session = fields.Float(string=u'Coût total',digits=(6, 2))
    observations = fields.Text(string='Observations')
