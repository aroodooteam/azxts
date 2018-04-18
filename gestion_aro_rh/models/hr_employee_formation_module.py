# -*- coding: utf-8 -*-

from openerp import fields, models


class hrEmployeeFormationModule(models.Model):

    _inherit = 'hr.employee.formation.module'

    branche_id = fields.Many2one('hr.employee.branche', string='Branche')
    specialite = fields.Char(string=u'Spécialité')
