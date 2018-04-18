# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class SubscriptionRiskDescription(models.Model):
    _name = 'subscription.risk.description'
    _description = 'Value corresponding to each risk description'

    name = fields.Char(string='Item')
    code = fields.Char(string='Code')
    value = fields.Char(string='Value')
    risk_line_id = fields.Many2one(comodel_name='aro.insurance.subscription.risk.line', string='Risk line')

