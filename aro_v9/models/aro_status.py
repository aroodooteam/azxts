# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroStatus(models.Model):
    _name = 'aro.status'
    _description = 'Aro status'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    _sql_constraints = [
                ('code', 'unique(code)', 'Code must be unique.'),
    ]
