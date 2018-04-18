# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class TypeRiskWarrantyTemplate(models.Model):
    _name = 'type.risk.warranty.template'
    _description = 'Template to use by default when loading type of risk'

    name = fields.Char(string='Name', help='Name of template')
    type_risk_id = fields.Many2one(comodel_name='aro.type.risque', string='Type Risk')
    is_default = fields.Boolean(string='Default Template')
    warranty_line_tmpl_ids = fields.One2many(comodel_name='warranty.line.template', inverse_name='risk_warranty_tmpl_id', string='Warranty Line Template')

