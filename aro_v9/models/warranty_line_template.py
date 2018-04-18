# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class WarrantyLineTemplate(models.Model):
    _name = 'warranty.line.template'
    _description = 'Template of risk detail in subscription'

    name = fields.Char(string='Description')
    risk_warranty_tmpl_id = fields.Many2one(comodel_name='type.risk.warranty.template', string='Warranty template')
    type_risk_id = fields.Many2one(comodel_name='aro.type.risque', string='Type Risk', related='risk_warranty_tmpl_id.type_risk_id')
    warranty_id = fields.Many2one(comodel_name='product.product', string='Warranty', domain="[('type_risque_id', '=', type_risk_id)]")
