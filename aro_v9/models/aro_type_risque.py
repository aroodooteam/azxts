# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class AroTypeRisque(models.Model):
    _name = 'aro.type.risque'
    _description = 'Insurance type of risk'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='Code', required=True)

    produit_assurance_id = fields.Many2one(
        string='Insurance Product',
        required=True,
        comodel_name='aro.produit.assurance')
