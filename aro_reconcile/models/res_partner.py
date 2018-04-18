# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class ResPartner(models.Model):
    _inherit = 'res.partner'

    master_group = fields.Boolean(string='Is Master of group')
    master_group_id = fields.Many2one(comodel_name='res.partner', string='Master')

    @api.multi
    def get_childs(self):
        child_ids = self.search([('master_group_id', '=', self.id)]).ids
        return {
            'type': 'ir.actions.act_window',
            'name': _('Partners'),
            'res_model': 'res.partner',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'target': 'current',
            'nodestroy': True,
            'domain': [('id', 'in', child_ids)]
        }
