# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroTypeRisqueClause(models.Model):
    _name = 'aro.type.risque.clause'
    _description = 'Clause of insurance type of risk'
    _order = "name asc"

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    description = fields.Text(string='Clause description')
    type_risque_id = fields.Many2one(comodel_name='aro.type.risque',
                                     string='Type of risk')
