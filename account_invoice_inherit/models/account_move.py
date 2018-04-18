# -*- coding: utf-8 -*-

from openerp import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    num_police = fields.Char(string='Police number')
    num_quittance = fields.Char(string='Quittance Number')
    date_effect = fields.Date(string='Effective Date')
    date_end = fields.Date(string='Contract End Date')
