# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrSessionElearning(models.Model):
    _name = 'hr.session.elearning'


    plan_formation_id = fields.Many2one('hr.plan.elearning', string=u'Libellé')
    plan_formation_objectif_id = fields.Char(related='plan_formation_id.objectif_id.name', readonly=True, string='Objectif')
    plan_formation_module_id = fields.Char(related='plan_formation_id.module_id.name', readonly=True, string='Module')
    branche = fields.Char(string='Branche')
    #plan_formation_branche_id = fields.Char(related='plan_formation_id.branche_id.name', readonly=True,string='Branche')
    date_debut_session = fields.Date(string=u'Date Début')
    date_fin_session = fields.Date(string='Date Fin')
    instructor_id = fields.Many2one('res.partner', string='Animateur')
    attendee_ids = fields.Many2many('hr.employee', string='Attendee')
    cout_session = fields.Float(string=u'Coût', digits=(6,2))
