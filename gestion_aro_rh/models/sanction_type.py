# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class sanctionType(models.Model):

    _inherit = 'sanction.type'

    code_sanction = fields.Char(string='Code Sanction')
