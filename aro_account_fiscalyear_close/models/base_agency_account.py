# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class BaseAgencyAccount(models.Model):
    _name = 'base.agency.account'
    _description = 'List of account to be use for opening entries'

    name = fields.Many2one(comodel_name='account.account', string='Account')
    agency_id = fields.Many2one(comodel_name='base.agency', string='Agency')
