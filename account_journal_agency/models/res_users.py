# -*- coding: utf-8 -*-

from openerp import models, fields


class res_users(models.Model):
    _inherit = 'res.users'

    agency_id = fields.Many2one('base.agency',
                                related='employee_ids.agency_id')
