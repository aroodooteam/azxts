# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.addons.decimal_precision import decimal_precision as dp
import logging
logger = logging.getLogger(__name__)

class AroRegistrationFee(models.Model):

    _name = 'aro.registration.fee'

    name = fields.Char(
        string='Name',
        required=True,
    )

    code = fields.Char(
        string='Code',
        required=True,
    )

    date_debut = fields.Date(
        string='Date debut',
        required=True,
        default=fields.Date.context_today,
        help=False
    )

    date_fin = fields.Date(
        string='Date fin',
        required=False,
        default=fields.Date.context_today,
        help=False
    )

    tax_terfisc_id = fields.Many2one(
        string='Territoire fiscal',
        required=True,
        comodel_name='account.fiscal.position'
    )
    indice = fields.Float(
        string='Indice',
        required=True,
        default=0.0,
        digits_compute=dp.get_precision('Account'),
        help=False
    )
