# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
import logging
logger = logging.getLogger(__name__)

class AroCommission(models.Model):
    """Commissions"""
    _name = 'aro.commission'
    _description = 'Product insurance commission'

    com_date = fields.Date(
        string='Commission date',
        required=True,
        default=fields.Date.context_today,
    )

    com_police = fields.Char(
        string='Police',
        required=False,
    )

    com_type_apporteur = fields.Many2one(
        string='Com type apporteur',
        comodel_name='aro.type.apporteur',
    )

    type_emission_id = fields.Many2one(
        comodel_name='aro.type.emission',
        string='Emission', required=False
    )

    com_type_emission = fields.Char(
        string='Com type emmission',
        required=False,
    )

    com_taux = fields.Float(
        string='Com taux',
        required=True,
        default=0.0,
        digits=(16, 2),
    )

    aro_type_apporteur_id = fields.Many2one(comodel_name='aro.type.apporteur', required=True, string='Broker type')


