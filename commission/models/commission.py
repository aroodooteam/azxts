# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today NextHope Business Solutions
#    <contact@nexthope.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
from openerp import fields, models, api


class commission_commission(models.Model):
    _name = 'commission.commission'

    partner_commissioned = fields.Many2one('res.partner',
                                           string="commissionne")
    account_commission = fields.Many2one(
        'account.account',
        string="compte",
        domain=[('type', 'not in', ['view', 'closed'])])
    account_charge_commission = fields.Many2one(
        'account.account',
        string="compte de charge",
        domain=[('type', 'not in', ['view', 'closed'])])
    account_amount = fields.Float(string="montant")
    commission_invoice = fields.Many2one('account.invoice', string='Invoice')
    move_id = fields.Many2one('account.move', string='Journal Entry',
                              readonly=True, index=True, ondelete='restrict',
                              copy=False,
                              help="Link to the automatically generated \
                              Journal Items.")
    period_id = fields.Many2one('account.period', string='Period',
                                related='commission_invoice.period_id')
    comment = fields.Text(string='comment',
                          related='commission_invoice.comment')
    type_invoice = fields.Selection(string='Type Invoice',
                                    related='commission_invoice.type')
    invoice_bd_id = fields.Integer(string='Invoice ID',
                                   compute='compute_ids')
    invoice_mv_id = fields.Integer(string='Invoice Move ID',
                                   compute='compute_ids')

    @api.one
    def compute_ids(self):
        self.invoice_bd_id = self.commission_invoice.id
        self.invoice_mv_id = self.move_id.id
