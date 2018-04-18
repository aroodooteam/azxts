# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrFormationObjectif(models.Model):
    _name = 'hr.formation.objectif'

    name = fields.Char(string='Objectif')
