# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrEmployeeSanctionVersion2(models.Model):
    _inherit = 'hr.employee.sanction'
    _description = 'Description'

    # date=fields.Date(string='Date')
    # name = fields.Many2one('hr.employee',string='Employee')
    # type = fields.Many2one('sanction.type',string='Sanction Type')
    # description= fields.Text(string='Description')
