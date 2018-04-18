# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 kazacube (http://kazacube.com).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'Madagascar ARO - Accounting',
    'version': '1.0',
    'author': 'Haritiana Rakotomalala',
    'category': 'Localization/Account Charts',
    'description': u"""
This is the base module to manage the accounting chart for ARO.
=================================================================

Ce Module charge le modèle du plan de comptes standard de ARO et permet de
générer les états comptables aux normes de ARO (Bilan, CPC (comptes de
produits et charges), balance générale à 6 colonnes,
Grand livre cumulatif...).""",
    'website': 'http://www.aro.mg',
    'depends': ['base', 'account'],
    'data': [
        'security/ir.model.access.csv',
        # 'data/account_type.xml',
        'data/account_pcg_malagasy_aro.xml',
        'wizard/l10n_mg_wizard.xml',
        'data/l10n_mg_account_tax_code_template.xml',
        'data/l10n_mg_account_chart.xml',
        'data/l10n_mg_account_tax_template.xml',
        # 'data/l10n_mg_tax.xml',
        # 'data/l10n_mg_journal.xml',
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
