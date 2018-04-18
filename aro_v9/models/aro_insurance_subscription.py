# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
import logging
logger = logging.getLogger(__name__)


class AroInsuranceSubscription(models.Model):
    _name = 'aro.insurance.subscription'
    _description = 'Insurance subscription [Insurance contract]'

    name = fields.Char(string='Police', default='/', required=True)

    subscriber_id = fields.Many2one(
        comodel_name='res.partner',
        string='Subscriber', help='Select the subscriber',
        domain="[('customer', '=', True)]", required=True
    )
    property_account_position = fields.Many2one(
        comodel_name='account.fiscal.position', string='Fiscal Position',
    )

    insured_id = fields.Many2one(
        comodel_name='res.partner', required=True,
        string='Insured', help='Select the insured',)

    branch_id = fields.Many2one(
        comodel_name='aro.branche.assurance', string='Branch')

    produit_assurance_id = fields.Many2one(
        comodel_name='aro.produit.assurance', string='Produit',
        required=True, domain="[('branche_assurance_id', '=', branch_id)]")

    fraction_ids = fields.Many2many(
        comodel_name='aro.fraction.assurance', string='Fractions',
        related='produit_assurance_id.fraction_assurance_ids')

    fraction_id = fields.Many2one(
        comodel_name='aro.fraction.assurance', string='Fraction',
        domain="[('id', 'in', fraction_ids[0][2])]")

    status_id = fields.Many2one(
        comodel_name='aro.status', string='Status',
        default=lambda self: self.env.ref('aro_v9.status_devis').id)

    pol_dent = fields.Char(string='v9_id')

    date_creation = fields.Date(string='Creating date of the policy')

    date_modification = fields.Date(string='Date of last update')

    risk_line_ids = fields.One2many(
        comodel_name='aro.insurance.subscription.risk.line',
        inverse_name='subscription_id', string='Risks Type')

    amendment_line_ids = fields.One2many(
        comodel_name='aro.amendment.line', inverse_name='subscription_id',
        string='List of amendments')
    amendment_count = fields.Integer(
        compute='get_amendment_count', string='Amendment count')

    apporteur_id = fields.Many2one(
        comodel_name='res.apporteur', string='Broker',
        help='Initial broker of the contract')

    subscription_type_id = fields.Many2one(
        comodel_name='insurance.subscription.type', string='Type',
        default=lambda self: self.env.ref('aro_v9.type_standard').id)

    _sql_constraints = [
        ('name', 'unique(name)', 'Police number must be unique.'),
    ]


    @api.onchange('produit_assurance_id')
    def onchange_product_insurance(self):
        fraction_ids = self.produit_assurance_id.fraction_assurance_ids
        logger.info('fraction_ids = %s' % fraction_ids)
        if fraction_ids:
            self.fraction_id = fraction_ids.ids[0]

    @api.onchange('subscriber_id')
    def get_property_account_position(self):
        self.ensure_one()
        self.property_account_position = self.subscriber_id.property_account_position.id
        self.insured_id = self.subscriber_id.id

    @api.multi
    def get_amendment_count(self):
        amendment_line_obj = self.env['aro.amendment.line']
        amendment_count = amendment_line_obj.search_count([('subscription_id', '=', self.id)])
        self.amendment_count = amendment_count

    @api.multi
    def create_first_amendment(self):
        view_id = self.env.ref('aro_v9.view_aro_amendment_line_form').id
        ctx = self._context.copy()
        ctx['default_subscription_id'] = self.id
        ctx['default_is_last_situation'] = True
        ctx['version_type'] = 'new'
        # ctx['default_emission_id'] = self.env.ref('aro_v9.devis').id
        dates_comp = self.with_context(version_type='new').get_end_date()
        ctx['default_starting_date'] = dates_comp.get('start_date')
        ctx['default_ending_date'] = dates_comp.get('end_date')
        res = {
            'type': 'ir.actions.act_window',
            'name': _('New Amendment'),
            'res_model': 'aro.amendment.line',
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'context': ctx,
        }
        return res

    @api.multi
    def get_end_date(self, start_date=False):
        if not start_date:
            start_date = datetime.today()
        else:
            start_date = datetime.strptime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        end_date = start_date
        if self.fraction_id == self.env.ref('aro_v9.fraction_annual'):
            end_date = start_date + relativedelta(months=12)
        elif self.fraction_id == self.env.ref('aro_v9.fraction_half_yearly'):
            end_date = start_date + relativedelta(months=6)
        elif self.fraction_id == self.env.ref('aro_v9.fraction_quarterly'):
            end_date = start_date + relativedelta(months=3)
        elif self.fraction_id in (self.env.ref('aro_v9.fraction_monthly'),self.env.ref('aro_v9.fraction_unique')):
            end_date = start_date + relativedelta(months=1)
        if self._context.get('version_type') != 'new':
            start_date = start_date + timedelta(days=1)
        end_date = end_date - timedelta(days=1)
        res = {
            'end_date': datetime.strftime(end_date, DEFAULT_SERVER_DATE_FORMAT),
            'start_date': datetime.strftime(start_date, DEFAULT_SERVER_DATE_FORMAT)
        }
        return res

    @api.multi
    def renew_amendment(self):
        resilie = self.env.ref('aro_v9.status_resilie').id
        devis = self.env.ref('aro_v9.status_devis').id
        if self.status_id.id == resilie:
            raise exceptions.Warning(_('You can\'t renew contract closed'))
        elif self.status_id.id == devis:
            raise exceptions.Warning(_('You can\'t renew unvalidated contract'))
        res = {}
        ctx = self._context.copy()
        ctx['default_subscription_id'] = self.id
        if not ctx.get('version_type', False):
            ctx['version_type'] = 'renew'
        # logger.info('\n === ctx version = %s' % ctx['version_type'])
        ctx['default'] = True
        # logger.info('\n === ctx = %s' % self.ending_date)
        amendment_line_obj = self.env['aro.amendment.line']
        amendment_line_ids = amendment_line_obj.search([('subscription_id', '=', self.id), ('is_last_situation', '=', True)])
        if not amendment_line_ids or len(amendment_line_ids) > 1:
            raise exceptions.Warning(_('Sorry, You don\'t have or you get more than one amendment defined as last situation.\n Fix it first before continuing'))
        else:
            logger.info('\n === ending_date = %s' % amendment_line_ids.ending_date)
            copy_vals = amendment_line_ids.with_context(ctx)._get_all_value()
            ctx.update(parent_amendment_line=amendment_line_ids.id)
            copy_vals.update(default_is_last_situation=True)
            copy_vals.update(default_emission_id=self.env.ref('aro_v9.renouvellement').id)
            copy_vals.update(default_parent_id=amendment_line_ids.id)
            new_date = self.get_end_date(amendment_line_ids.ending_date)
            copy_vals.update(default_starting_date=new_date.get('start_date'))
            copy_vals.update(default_ending_date=new_date.get('end_date'))
            # logger.info('\n === copy_vals = %s' % copy_vals)
            # copy_vals.update(default_ending_date=self.get_end_date(self))
            ctx.update(copy_vals)
            view_id = self.env.ref('aro_v9.view_aro_amendment_line_form').id
            res.update({
                'type': 'ir.actions.act_window',
                'name': _('Renew'),
                'res_model': 'aro.amendment.line',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id],
                # 'res_id': new_amendment.id,
                'context': ctx,
                'target': 'current',
                'flags': {'form': {'action_buttons': True, 'options': {'mode': 'edit'}}},
            })
        return res

    @api.multi
    def update_subscription(self):
        """ Update subscription : Avenant """
        amendment_line_obj = self.env['aro.amendment.line']
        res = self.with_context(version_type='amendment').renew_amendment()
        ctx = res.get('context', {})
        res.update(name=_('Amendment'))
        logger.info('\n === parent_id = %s' % ctx.get('default_parent_id', False))
        amendment_line_id = ctx.get('default_parent_id', False)
        amendment_line_id = amendment_line_obj.browse(amendment_line_id)
        ctx.update(default_starting_date=amendment_line_id.starting_date)
        ctx.update(default_ending_date=amendment_line_id.ending_date)
        ctx.update(default_emission_id=self.env.ref('aro_v9.avenant').id)
        res.update(context=ctx)
        return res

    # TODO
    @api.multi
    def cancel_subscription(self):
        res = False
        amendment_line_obj = self.env['aro.amendment.line']
        res = self.with_context(version_type='terminate').renew_amendment()
        ctx = res.get('context', {})
        res.update(name=_('Terminate'))
        amendment_line_id = ctx.get('default_parent_id', False)
        amendment_line_id = amendment_line_obj.browse(amendment_line_id)
        ctx.update(default_starting_date=amendment_line_id.starting_date)
        ctx.update(default_ending_date=amendment_line_id.ending_date)
        ctx.update(default_emission_id=self.env.ref('aro_v9.resiliation').id)
        res.update(context=ctx)

        return res

    # TODO
    @api.multi
    def suspend_subscription(self):
        """ Suspend subscription : Suspension """
        amendment_line_obj = self.env['aro.amendment.line']
        res = self.with_context(version_type='suspend').renew_amendment()
        ctx = res.get('context', {})
        res.update(name=_('Pending'))
        amendment_line_id = ctx.get('default_parent_id', False)
        amendment_line_id = amendment_line_obj.browse(amendment_line_id)
        ctx.update(default_starting_date=amendment_line_id.starting_date)
        ctx.update(default_ending_date=amendment_line_id.ending_date)
        ctx.update(default_emission_id=self.env.ref('aro_v9.suspension').id)
        res.update(context=ctx)
        return res

    # TODO
    @api.multi
    def reinstatement_subscription(self):
        """ Reinstatment : d'abord voir si police suspendue """
        status_id = self.env.ref('aro_v9.status_suspendu')
        if self.status_id != status_id:
            raise exceptions.Warning(_('Sorry, You don\'t have to reinstate a subscription which is not suspended'))
        else:
            amendment_line_obj = self.env['aro.amendment.line']
            res = self.with_context(version_type='reinstatement').renew_amendment()
            ctx = res.get('context', {})
            res.update(name=_('Reinstatment'))
            amendment_line_id = ctx.get('default_parent_id', False)
            amendment_line_id = amendment_line_obj.browse(amendment_line_id)
            ctx.update(default_starting_date=amendment_line_id.starting_date)
            ctx.update(default_ending_date=amendment_line_id.ending_date)
            ctx.update(default_emission_id=self.env.ref('aro_v9.remise_en_vigueur').id)
            res.update(context=ctx)
            return res

    @api.multi
    def get_current_version(self):
        res = {}
        amendment_line_obj = self.env['aro.amendment.line']
        domain = [('is_last_situation', '=', True), ('subscription_id', '=', self.id)]
        amendment_line_id = amendment_line_obj.search(domain)
        if not amendment_line_id:
            raise exceptions.Warning(_('Sorry, there is no recent version for this contract'))
        view_id = self.env.ref('aro_v9.view_aro_amendment_line_form').id
        res.update({
                'type': 'ir.actions.act_window',
                'name': _('Last Version'),
                'res_model': 'aro.amendment.line',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [view_id],
                'res_id': amendment_line_id.id,
                'target': 'current',
            })
        return res

    @api.multi
    def get_having_right(self):
        family_obj = self.env['res.partner.family']
        domain = [('partner_id', '=', self.insured_id.id)]
        family = family_obj.search(domain)
        context = self._context.copy()
        context.update(default_partner_id=self.insured_id.id)
        action_id = self.env.ref('aro_v9.act_open_res_partner_family_view')
        actions = action_id.read()[0]
        actions.update({
            'domain': [('id', 'in', family.ids)],
            'context': context,
        })
        return actions
