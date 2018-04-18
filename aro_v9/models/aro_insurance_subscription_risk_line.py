# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)


class AroInsuranceSubscriptionRiskLine(models.Model):
    _name = 'aro.insurance.subscription.risk.line'
    _description = 'Subscription line (Content list of risk type)'

    @api.depends('insured_id')
    @api.multi
    def _get_partner_right(self):
        if not self.insured_id:
            return False
        family_obj = self.env['res.partner.family']
        family_ids = family_obj.search([('partner_id', '=', self.insured_id.id)])
        having_right = self.insured_id
        having_right += family_ids.mapped('name')
        self.have_right_ids = having_right
        return {
            'domain': {
                'partner_id': [('id', 'in', having_right.ids)]
            }
        }

    @api.onchange('insured_id')
    def onchange_insured(self):
        if not self.insured_id:
            return False
        self.partner_id = self.insured_id
        return {
            'domain': {
                'partner_id': [('id', 'in', self.have_right_ids.ids)]
            },
        }

    name = fields.Char(string='Description')
    subscription_id = fields.Many2one(comodel_name='aro.insurance.subscription', string='Subscription')
    amendment_line_id = fields.Many2one(comodel_name='aro.amendment.line', string='Amendment Line')
    produit_assurance_id = fields.Many2one(comodel_name='aro.produit.assurance', string='Insurance Product', related='subscription_id.produit_assurance_id')
    type_risk_id = fields.Many2one(comodel_name='aro.type.risque', string='Risk', domain="[('produit_assurance_id', '=', produit_assurance_id)]")
    warranty_line_ids = fields.One2many(comodel_name='risk.warranty.line', inverse_name='risk_id', string='Warranty')
    risk_description_ids = fields.One2many(comodel_name='subscription.risk.description', inverse_name='risk_line_id', string='Risk description')
    risk_warranty_tmpl_id = fields.Many2one(comodel_name='type.risk.warranty.template', string='Template', domain="[('type_risk_id', '=', type_risk_id)]")
    insured_id = fields.Many2one(comodel_name='res.partner', string='Insured', related='subscription_id.insured_id')
    have_right_ids = fields.One2many(comodel_name='res.partner', string='Having right', compute='_get_partner_right', store=False)
    partner_id = fields.Many2one(comodel_name='res.partner', string='Partner')

    @api.onchange('amendment_line_id')
    def onchange_amendment_line(self):
        self.subscription_id = self.amendment_line_id.subscription_id.id

    # TODO
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update(name="%s" % (self.name or ''))
        res = super(AroInsuranceSubscriptionRiskLine, self).copy(default)
        new_warranty_line = False
        for warranty_line_id in self.warranty_line_ids:
            if not new_warranty_line:
                new_warranty_line = warranty_line_id.copy()
                new_warranty_line.write({'risk_id': res.id})
            else:
                new_warranty_line_buf = warranty_line_id.copy()
                new_warranty_line_buf.write({'risk_id': res.id})
                new_warranty_line += new_warranty_line_buf
        logger.info('res = %s' % res)
        return res

    @api.onchange('type_risk_id')
    def onchange_type_risk(self):
        if not self.type_risk_id:
            return False
        description_obj = self.env['aro.type.risque.description']
        desc_ids = description_obj.search([('type_risque_id', '=', self.type_risk_id.id)])
        all_desc = []
        tmpl_obj = self.env['type.risk.warranty.template']
        tmpl_id = tmpl_obj.search([('type_risk_id', '=', self.type_risk_id.id), ('is_default', '=', True)], limit=1)
        for desc_id in desc_ids:
            all_desc.append(
                (0, 0, {'code': desc_id.code, 'name': desc_id.name,})
            )
            self.update({'risk_description_ids': all_desc, 'risk_warranty_tmpl_id': tmpl_id.id if tmpl_id else False})

    # TODO
    @api.onchange('risk_warranty_tmpl_id')
    def onchange_risk_warranty_template(self):
        if not self.risk_warranty_tmpl_id or not self._context:
            return False
        # tmpl_obj = self.env['type.risk.warranty.template']
        # tmpl_id = tmpl_obj.search([('type_risk_id', '=', self.type_risk_id), ('is_default', '=', True)], limit=1)
        all_tmpl = []
        for tmpl_id in self.risk_warranty_tmpl_id.warranty_line_tmpl_ids:
            all_tmpl.append(
                (0, 0, {'warranty_id': tmpl_id.warranty_id.id, 'name': tmpl_id.name,})
            )
            self.update({'warranty_line_ids': all_tmpl})
        logger.info(' \n === onchange warranty template')
