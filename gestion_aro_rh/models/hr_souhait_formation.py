# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrSouhaitFormation(models.Model):
    _name = 'hr.souhait.formation'

    employee_id= fields.Many2one('hr.employee', string='Nom du demandeur')
    name= fields.Many2one('hr.employee', string='Nom du demandeur')
    employee_department_id = fields.Char(related='name.department_id.name', readonly=True, string=u'Unité')
    employee_job_id = fields.Char(related='name.job_id.name', readonly=True, string='Fonction')
    anciennete = fields.Integer(string=u'Ancienneté au poste')
    souhait_detail_ids = fields.One2many('hr.souhait.detail', 'employee_id', string=u'Détail')
