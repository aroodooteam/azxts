# -*- coding: utf-8 -*-

from openerp import models, api, fields, exceptions


class ProductCategory(models.Model):
    _inherit = 'product.category'

    code = fields.Char(string='Code', size=32)

