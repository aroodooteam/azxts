# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrEmployee(models.Model):

    _inherit = 'hr.employee'

    career_ids=fields.One2many('hr.employee.career','employee_id',string='Career')
    # sanction_version_2_ids = fields.One2many('hr.employee.sanction.version','name',string='Sanctions')
    #session_formation_version_ids = fields.One2many('hr.session.formation.version_2','employee_id',string='Sessions')
    session_formation_ids = fields.Many2many('hr.session.formation.version_2',string='Session de formation')
    session_plan_formation_3_ids = fields.Many2many('hr.session.plan.version_3',string='Session de formation')
    session_elearning_ids = fields.Many2many('hr.session.elearning',string=u'E-learning')
    diplome_ids = fields.One2many('hr.employee.diplome','employee_id',string=u'Diplômes')
