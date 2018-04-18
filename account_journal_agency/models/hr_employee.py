# -*- coding: utf-8 -*-

from openerp import models, fields


class hr_employee(models.Model):
    _inherit = 'hr.employee'

    agency_id = fields.Many2one('base.agency', 'Agence')
