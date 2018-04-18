# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)
from . import agency_account as agac
from openerp import api, exceptions, fields, models, _


class BaseAgency(models.Model):
    _inherit = 'base.agency'

    account_ids = fields.One2many(comodel_name='base.agency.account', inverse_name='agency_id', string='Agency')

    @api.multi
    def import_account(self):
        account_obj = self.env['account.account']
        agac_obj = self.env['base.agency.account']
        agac_ids = agac_obj.search([('agency_id', '=', self.id)])
        agac_ids.unlink()
        for k,v in agac.ALL_AGENCY.iteritems():
            if k[-2:] == self.code:
                for account in account_obj.search([('code', 'in', v)]):
                    agac_obj.create({"name": account.id, "agency_id": self.id})
