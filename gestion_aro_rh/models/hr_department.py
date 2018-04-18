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

from openerp import models, fields


class HrDepartment(models.Model):

    _inherit = 'hr.department'


    code_service = fields.Char(string='Code Service', size=8, required=True)
    niveau = fields.Integer(string='Niveau')
    abreviation = fields.Char(string=u'Abréviation', size=8)
    rattachement = fields.Char(string='Rattachement', size=8)
    date = fields.Date(string='Date')
    service_gestion = fields.Char(string='Service de Gestion', size=8)
    code_analytique = fields.Char(string='Code Analytique', size=8)
    compte_passage = fields.Char(String='Compte de Passage', size=8)
    compte_agence = fields.Char('Compte Agence', size=8)
    service_param_paye = fields.Char(string='Service Param Paye', size=8)
    active = fields.Boolean(string='Active', default=True)
