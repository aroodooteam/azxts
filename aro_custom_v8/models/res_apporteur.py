# -*- coding: utf-8 -*-

from openerp import models, api, fields


class ResApporteur(models.Model):
    _name = 'res.apporteur'
    _inherits = {'res.partner': 'partner_id'}
    _description = ''

    partner_id = fields.Many2one('res.partner', string='Related Partner',
                                 required=True,
                                 ondelete='restrict', auto_join=True,
                                 help='Partner-related data of apporteur')
    name = fields.Char(related='partner_id.name', inherited=True)
    agency_id = fields.Many2one(related='partner_id.agency_id', inherited=True)
    title = fields.Many2one(related='partner_id.title', inherited=True)
    ap_code = fields.Char(string='AP code', size=8)
    serial_identification = fields.Char(string='Serial Id', size=8)
    statut = fields.Char(string='Statut', size=16)
    linked_account_ids = fields.One2many('res.apporteur.compte',
                                         'apporteur_id',
                                         string='Apporteur account')
    is_under_agency = fields.Boolean(string='Under Agency')
    ua_code = fields.Char(string='UA Code', size=16)
    ref_apporteur = fields.Char(string='Reference', size=16)
    account_charge_vie_id = fields.Many2one('account.account', string='Expense Account Life')
    account_charge_id = fields.Many2one('account.account', string='Expense Account')

    _defaults = {
        'customer': False,
    }

    @api.multi
    def ref_to_partner(self):
        for app in self:
            if not app.partner_id.ref:
                app.partner_id.ref = app.ref_apporteur

    # @api.model
    # def create(self, vals):
        # res = super(ResApporteur, self).create(vals)
        # if res.is_under_agency:
            # res.partner_id.update({'customer': False})
        # return res

    @api.model
    def update_partner_linked(self):
        for app in self.search([]):
            app.partner_id.ref = app.ref_apporteur


class ResApporteurCompte(models.Model):
    _name = 'res.apporteur.compte'
    _description = u"""Liste des comptes de l'apporteur
    dans les différents agence"""

    apporteur_id = fields.Many2one('res.apporteur', string='Apporteur',
                                   required=True)
    agency_id = fields.Many2one('base.agency', required=True)
    ap_code = fields.Char(string='AP code', size=8)
    serial_identification = fields.Char(string='Serial Id', size=8)
