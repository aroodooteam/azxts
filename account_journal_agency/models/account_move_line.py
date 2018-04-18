# -*- coding: utf-8 -*-

from openerp import models, fields


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    agency_id = fields.Many2one('base.agency', related='journal_id.agency_id',
                                store=True)
