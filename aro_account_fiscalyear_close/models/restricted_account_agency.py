# -*- coding: utf-8 -*-

from openerp import api, fields, models, exceptions, _
import agency_account
import logging
logger = logging.getLogger(__name__)

ACCOUNT_SIEGE = ['101301', '105001', '105002', '105003', '106301', '106403', '106801', '106802', '110001', '110002', '165231', '171001', '171205', '171801', '171805', '172205', '172801', '210001', '212101', '212201', '230201', '230205', '231302', '232603', '232605', '232607', '232608', '232611', '232612', '232613', '233500', '233505', '233507', '233600', '233603', '233605', '251201', '251501', '263101', '263103', '263201', '263203', '293360', '295101', '300101', '300102', '312101', '312901', '315101', '320501', '320502', '320801', '332001', '335001', '391211', '391515', '391801', '393501', '393505', '393801', '393805', '400000', '400800', '404000', '408000', '410999', '423001', '424850', '425100', '426100', '432001', '432006', '443003', '443006', '444101', '444102', '445711', '447001', '447002', '447005', '457101', '463100', '466010', '466050', '466500', '466550', '468005', '468013', '468014', '470201', '470400', '4780003', '4780011', '4780012', '4780040', '4780084', '483100', '483111', '483120', '483121', '483921', '486001', '487301', '487701', '487702', '487703', '487704', '490801', '492901', '496102', '504301', '504302', '510101', '510102', '511101', '511201', '511202', '511301', '511302', '511303', '511305', '511310', '511321', '511322', '511323', '511324', '511325', '511326', '511327', '512304', '512307', '512403', '512404', '512405', '512502', '513103', '513105', '513106', '513200', '521001', '521002', '521003', '521005', '521020', '521100', '52209901', '52209902', '52209903', '52209905', '52209906', '52209908', '52209910', '52209911', '52209912', '52209913', '52209914', '52209915', '52209916', '52209917', '52209920', '52209921', '52209922', '52209927', '52209928', '52209929', '52219907', '52219919', '52219936', '52219937', '52219939', '52249902', '53009901', '53009902', '53009903', '53009904', '590302', '590401', '591121', '591122', '591131', '591132', '591133', '591134', '591135', '591141', '591147', '591151', '591152', '591153', '591154', '591155', '591156', '591157']

ACCOUNT_AMPEFILOHA = []


class RestrictedAccountAgency(models.Model):
    _name = 'restricted.account.agency'
    _description = '''Account should be used only for specified agency when
    generating opening entries'''

    name = fields.Many2one(comodel_name='base.agency', string='Agency', required=True)
    account_ids = fields.Many2many(comodel_name='account.account', string='Accounts')

    @api.model
    def insert_all_account(self):
        for elts in agency_account.ALL_AGENCY.keys():
            logger.info('elts = %s' % elts)
            self.set_account_siege(agency_account.ALL_AGENCY.get(elts), elts[-2:])

    # def set_account_siege(self, agence=agency_account.ADEMA86, code='86'):

    @api.model
    def set_account_siege(self, agence=[], code=False):
        if not agence or not code:
            raise exceptions.Warning(_('Please specify agency and code'))
        agency_obj = self.env['base.agency']
        account_obj = self.env['account.account']

        siege = agency_obj.search([('code', '=', code)])
        account_ids = account_obj.search([('code', 'in', agence)])
        logger.info('acc_ids = %s' % len(account_ids))
        vals = {
            'name': siege.id,
            'account_ids': [(4, account_ids.ids)]
        }
        raa_id = self.search([('name', '=', siege.id)])
        raa_id.unlink()
        raa_id = False
        if not raa_id:
            self.create(vals)
        # else:
        #     vals['account_ids'] = [(4, account_ids.ids)]
        #     self.write(vals)
