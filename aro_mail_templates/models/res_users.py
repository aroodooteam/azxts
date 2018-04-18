# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _
from openerp.addons.auth_signup.res_users import now
import logging
logger = logging.getLogger(__name__)


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        print(" inh_context_action_reset_password = %s" % self._context)
        # prepare reset password signup
        res_partner = self.env['res.partner']
        partner_ids = [user.partner_id.id for user in self]
        partner_ids = res_partner.browse(partner_ids)
        partner_ids.with_context(self._context).signup_prepare(signup_type="reset", expiration=now(days=+1))

        context = dict(self._context or {})

        # send email to users with their signup url
        template = False
        if context.get('create_user'):
            try:
                template = self.env.ref('aro_mail_templates.aro_set_password_email')
            except ValueError:
                pass
        if not bool(template):
            template = self.env.ref('aro_mail_templates.aro_reset_password_email')
        assert template._name == 'email.template'
        logger.info('template = %s' % template._name)

        for user in self:
            if not user.email:
                raise exceptions.Warning(_('Cannot send email: user has no email address. %s' % user.name))
            context['lang'] = user.lang  # translate in targeted user language
            template.with_context(context).send_mail(user.id, force_send=True, raise_exception=True)

