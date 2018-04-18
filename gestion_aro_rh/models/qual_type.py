# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class qualType(models.Model):

    _inherit = 'qual.type'

    niveau_id = fields.Many2one('hr.niveau.etudes', string='Niveau')
