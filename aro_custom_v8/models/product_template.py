# -*- coding: utf-8 -*-

from openerp import models, api, fields, exceptions


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    code = fields.Char(string='Code', size=32)
    sinistre_account_id = fields.Many2one('account.account', string='Claim Account', help='Account reserved for sinister')
    commission_account_id = fields.Many2one('account.account', string='Commission Account', help='Account reserved for commission')
    recours_account_id = fields.Many2one('account.account', string='Recours Account', help='Account reserved for recours')
