# -*- coding: utf-8 -*-

from openerp import fields, models
from openerp.addons.decimal_precision import decimal_precision as dp


class AroTaxe(models.Model):

    """ aro taxe"""

    #_inherit = ['account.fiscal.position']

    _name = 'aro.taxe'
    _description = 'Insurance tax'

    tax_date = fields.Datetime(
        string='Tax date', required=True,
        default=fields.datetime.now(),
        help='Date De la taxe en vigueur')

    tax_te = fields.Float(
        string='Tax te',
        required=False,
        digits_compute=dp.get_precision('Account'),
        help='tax Te'
    )

    tax_te_id = fields.Many2one(
        comodel_name='account.tax', 
        string='TE',
        required=True,
        domain='[("description", "like", "Te%")]'
    )

    tax_tva = fields.Float(
        string='Tax TVA',
        digits_compute=dp.get_precision('Account'),
        required=False,
        help='Tax TVA'
    )

    tax_tva_id = fields.Many2one(
        comodel_name='account.tax',
        string='VAT',
        required=True,
        domain='[("description", "like", "Tva-20.0")]'
    )

    tax_terfisc_id = fields.Many2one(
        string='Territoire fiscal',
        required=True,
        comodel_name='account.fiscal.position'
    )

    product_id = fields.Many2one(comodel_name='product.template', string='Warranty', help='Warranty')
