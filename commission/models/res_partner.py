# -*- coding: utf-8 -*-

from openerp import models, fields


class res_partner(models.Model):
    # Inherits partner and adds invoice information in the partner form
    _inherit = 'res.partner'

    id_intermediaire = fields.Integer(string="Intermediaire")
    id_apporteur = fields.Integer(string="Apporteur")
