# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrFormationInstructor(models.Model):
    _name = 'hr.formation.instructor'


    name = fields.Char(string='Formateur')
    societe = fields.Char(string=u'Société')
    function = fields.Char(string=u'Poste occupé')
    phone = fields.Char(string=u'Tèl.', size=16)
    mobile = fields.Char(string=u'Tèl portable', size=16)
    email = fields.Char(string='Courriel')
