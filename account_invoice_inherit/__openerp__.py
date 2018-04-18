# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today NextHope Business Solutions
#    <haryoran04@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
{
    'name': 'Account Invoice Gestion assurance Inherit',
    'version': '1.0',
    'category': 'ARO',
    'description': """
Ce module hérite du module Account Invoice d'odoo. Il est utilisé pour mettre
à jour le champ dans la facture
===========================================

""",
    'depends': ['base', 'product', 'account'],
    'website': 'http://www.aro.mg',
    'author': 'Rakotomalala Haritiana Maminiaina',
    'data': [
        'views/account_invoice_view.xml',
        'views/account_move_view.xml',
    ],
    'auto_install': False,
    'installable': True,
}
