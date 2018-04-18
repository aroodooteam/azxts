# -*- coding: utf-8 -*-

from openerp import models, fields


class base_agency(models.Model):
    _name = 'base.agency'
    _inherits = {'res.partner': 'partner_id'}

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True,
                                 ondelete='restrict', auto_join=True,
                                 help='Partner-related data to agency')
    name = fields.Char(related='partner_id.name', inherited=True,
                       string='Agence')
    code = fields.Char('Code', size=4)
    parent_id = fields.Many2one('base.agency', 'Agence de gestion')
    is_agency_parent = fields.Boolean(string='Est une Agence de gestion',
                                      help='Check if parent of another')
    have_opening_journal = fields.Boolean(string='Have opening journal', help='Check if this agency should get an opening journal')
    active = fields.Boolean(string='Active', default=True)
