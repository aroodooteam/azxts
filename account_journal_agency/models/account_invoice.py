# -*- coding: utf-8 -*-

from openerp import models, fields


class account_invoice(models.Model):
    _inherit = 'account.invoice'

    agency_id = fields.Many2one('base.agency', related='journal_id.agency_id',
                                store=True)
