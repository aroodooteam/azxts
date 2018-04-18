# -*- coding: utf-8 -*-

from openerp import models, fields


class account_move_line(models.Model):
    _inherit = 'account.move.line'

    analytic1 = fields.Char(string="Analytique 1")
    analytic2 = fields.Char(string="Analytique 2")
