# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class InsuranceSubscriptionType(models.Model):
    """ Store all type of subscription"""
    _name = 'insurance.subscription.type'
    _description = 'Type of subscription'

    name = fields.Char(string='Name')
    code = fields.Char(string='Code')

