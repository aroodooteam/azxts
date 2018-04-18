# -*- coding: utf-8 -*-

from openerp import models, fields


class res_agency(models.Model):
    _name = 'res.agency'

    name = fields.Char(string='Nom')
    code = fields.Char(string='Code', size=10)
