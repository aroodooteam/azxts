# -*- coding: utf-8 -*-

from openerp import models, api, fields

class Newmenu(models.Model):
	_name = 'new.menu'

	name = fields.Char(string="Name")