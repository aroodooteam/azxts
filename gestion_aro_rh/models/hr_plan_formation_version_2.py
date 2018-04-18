# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrPlanFormationVersion2(models.Model):
    _name = 'hr.plan.formation.version_2'


    name = fields.Char(string=u'Libellé')
    session_formation_ids = fields.One2many('hr.session.formation.version_2', 'plan_formation_id', string='Sessions')
