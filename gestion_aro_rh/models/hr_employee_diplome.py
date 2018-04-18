# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _


class hrEmployeeDiplome(models.Model):
    _name = 'hr.employee.diplome'


    employee_id = fields.Many2one('hr.employee', string=u'Employé')
    ordre = fields.Char(string='Ordre')
    annee = fields.Integer(string=u'Année')
    diplome_id = fields.Many2one('qual.type', string=u'Diplôme')
    branche_id = fields.Many2one('hr.employee.branche', string='Branche')
    niveau = fields.Char(related='diplome_id.niveau_id.name', readonly=True, string='Niveau')
    specialite = fields.Char(string=u'Spécialité')
    lieu = fields.Char(string='Lieu')
