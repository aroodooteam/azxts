# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api
# from _dbus_bindings import String
import datetime
import logging
_logger = logging.getLogger(__name__)


class account_invoice(models.Model):

    _inherit = "account.invoice"

    pol_numpol = fields.Char(string="Numero Police")
    prm_datedeb = fields.Date(string="Date Effet Contrat")
    prm_datefin = fields.Date(string=u"Date Fin Contrat")
    prm_numero_quittance = fields.Char(string="Numero Quittance")
    # prm_ident_invoice = fields.Float()

    @api.multi
    def action_move_create(self):
        """ Creates invoice related analytics and financial move lines """

        res = super(account_invoice, self).action_move_create()

        for inv in self:
            if not inv.move_id:
                return res
            for ml in inv.move_id.line_id:
                ml_vals = {
                    'emp_police': inv.pol_numpol,
                    'emp_quittance': inv.prm_numero_quittance,
                    'emp_effet': datetime.datetime.strptime(inv.prm_datedeb, '%Y-%m-%d').date() if inv.prm_datedeb else datetime.datetime.today(),
                    'emp_datech': datetime.datetime.strptime(inv.prm_datefin, '%Y-%m-%d').date() if inv.prm_datefin else datetime.datetime.today(),
                }
                ml.update(ml_vals)
            move_vals = {
                'num_police': inv.pol_numpol,
                'num_quittance': inv.prm_numero_quittance,
                'date_effect': datetime.datetime.strptime(inv.prm_datedeb, '%Y-%m-%d').date() if inv.prm_datedeb else datetime.datetime.today(),
                'date_end': datetime.datetime.strptime(inv.prm_datefin, '%Y-%m-%d').date() if inv.prm_datefin else datetime.datetime.today(),
            }
            inv.move_id.update(move_vals)
        self._log_event()
        return res
