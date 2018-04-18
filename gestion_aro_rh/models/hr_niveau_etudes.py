# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrNiveauEtudes(models.Model):
     _name = 'hr.niveau.etudes'

     niveau = fields.Integer(string='Level')
     name = fields.Char(string=u'Name')
