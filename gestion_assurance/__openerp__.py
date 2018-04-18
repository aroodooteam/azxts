# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today NextHope Business Solutions <contact@nexthope.net>
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
    'name': 'gestion_assurance',
    'version': '1.0',
    'category': 'ARO',
    'description': """
This is the module used on ARO database test.
===========================================

**Credits:** NextHope.
""",
    'depends': ['base','product','account'],
    'website': 'http://www.nexthope.net',
    'author': 'NextHope',
    'data': [
        'views/police_view.xml',
		'views/account_invoice_view.xml',		
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
}
