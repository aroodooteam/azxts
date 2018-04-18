# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.addons.decimal_precision import decimal_precision as dp


class AroProduitAssurance(models.Model):
    _name = 'aro.produit.assurance'
    _description = 'Insurance product'

    name = fields.Char(string='Name', required=True)
    code = fields.Char(string='code', required=True)
    pas_ident = fields.Char(string='Old ID')
    amount_accessories = fields.Float(string='Accessories Amount',
                                      digits_compute=dp.get_precision('Account'),
                                      help='Default Accessories amount')
    amount_accessories_nb = fields.Float(string='Accessories Amount per object',
                                      digits_compute=dp.get_precision('Account'),
                                      help='Default Accessories amount if more than one object')
    amount_threshold = fields.Float(string='Threshold amount',
                                    digits_compute=dp.get_precision('Account'),
                                    help='Limit of amount')
    pas_num_module = fields.Integer(string='Module number')
    price = fields.Char(string='Prices')
    image = fields.Binary(string='Logo', attachment=True, help='Image size is limited to 1024px1024px')
    image_medium = fields.Binary(string='Medium-sized image', attachment=True, help='Image size is limited to 128px128px')
    image_small = fields.Binary(string='Small-sized image', attachment=True, help='Image size is limited to 64px64px')
    branche_assurance_id = fields.Many2one(comodel_name='aro.branche.assurance', required=True, string='Insurance branch')
    fraction_assurance_ids = fields.Many2many(comodel_name='aro.fraction.assurance', string='Fraction Insurance', required=True)
    comments = fields.Text(string='Comments')
