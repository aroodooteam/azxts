# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
import logging
logger = logging.getLogger(__name__)


class PartnerGroupWiz(models.TransientModel):
    _name = 'partner.group.wiz'
    _description = 'Wizard allowing group partner'

    @api.multi
    def group_selected_partner(self):
        active_ids = self._context.get('active_ids')
        partner_obj = self.env['res.partner']
        partner_ids = partner_obj.browse(active_ids)
        partner_master = partner_obj.search([('id', 'in', active_ids),('master_group', '=', True)])
        if len(partner_master) > 1:
            partner_master = partner_master.sorted(key=lambda r: r.id)
            primary_master = partner_master[0]
            second_masters = partner_master - primary_master
            second_masters_childs = partner_obj.search([('master_group_id', 'in', second_masters.ids)])
            if second_masters_childs:
                second_masters_childs.write({'master_group_id': primary_master.id})
            second_masters.write({'master_group': False, 'master_group_id': primary_master.id})
            partner_ids = partner_ids - partner_master
            partner_ids.write({'master_group_id': primary_master.id})
        elif len(partner_master) == 1:
            partner_ids = partner_ids - partner_master
            partner_ids.write({'master_group_id': partner_master.id})
        else:
            partner_ids = partner_ids.sorted(key=lambda r: r.id)
            partner_master = partner_ids[0]
            partner_ids[0].write({'master_group': True})
            partner_ids = partner_ids - partner_ids[0]
            partner_ids.write({'master_group_id': partner_master.id})
        return True

