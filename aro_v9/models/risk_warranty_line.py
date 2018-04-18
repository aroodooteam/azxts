# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)


class RiskWarrantyLine(models.Model):
    _name = 'risk.warranty.line'
    _description = 'Risk detail in subscription'

    name = fields.Char(string='Description')
    risk_id = fields.Many2one(comodel_name='aro.insurance.subscription.risk.line', string='Risk type')
    type_risk_id = fields.Many2one(comodel_name='aro.type.risque', string='Type Risk', related='risk_id.type_risk_id')
    warranty_id = fields.Many2one(comodel_name='product.product', string='Warranty', domain="[('type_risque_id', '=', type_risk_id)]")
    types = fields.Selection(selection=[('new', 'New'),('removed', 'Removed'),('untouched', 'Untouched')], string='Label', default='new', help='Default value is new')

    @api.onchange('warranty_id')
    def onchange_warranty(self):
        if not self.warranty_id:
            return False
        else:
            self.name = self.warranty_id.name
