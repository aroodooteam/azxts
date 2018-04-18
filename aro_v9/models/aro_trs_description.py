# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroTypeRisqueDescription(models.Model):
    _name = 'aro.type.risque.description'
    _description = 'Description of insurance type of risk'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)
    type_risque_id = fields.Many2one(comodel_name='aro.type.risque',
                                         string='Type of risk')
