# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroFractionAssurance(models.Model):
    _name = 'aro.fraction.assurance'
    _description = 'Product insurance fraction'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    _sql_constraints = [
        ('code', 'unique(code)', 'Code must be unique.'),
    ]
