# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroTypeEmission(models.Model):
    _name = 'aro.type.emission'
    _description = 'Emission type'
    _order = 'sequence ASC'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
                ('code', 'unique(code)', 'Code must be unique.'),
    ]
