# -*- coding: utf-8 -*-
from openerp import api, exceptions, fields, models, _


class hrSouhaitDetail(models.Model):
    _name = 'hr.souhait.detail'

    employee_id=fields.Many2one('hr.souhait.formation', string=u'Employé', readonly=True)
    competence = fields.Text(string=u'Compétence recherchée')
    formation_souhaitee = fields.Text(string=u'Formation souhaitée')
    date_envisagee=fields.Char(string=u'Période indicative')
    duree= fields.Char(string=u'Durée indicative')
    animateur=fields.Char(string='Animateur')
    avis_superieur=fields.Text(string=u'Avis du supérieur hiérarchique')
