# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class hrFormationParticipant(models.Model):
    _name = 'hr.formation.participant'


    #name = fields.Char(string='',size=64,required=False,readonly=False)
    participant_id = fields.Many2one('hr.employee',string='Participant',ondelete='cascade')
    session_formation_id = fields.Many2one('hr.session.formation.version_2', string='Session', ondelete='cascade')
