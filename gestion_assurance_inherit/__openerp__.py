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
    'name': 'Gestion assurance Inherit',
    'version': '1.0',
    'category': 'ARO',
    'description': """	
Ce module hérite du module Gestion assurance. Il est utilisé pour mettre
à jour le module Gestion assurance
===========================================

""",
    'depends': ['base','product','account'],
    'website': 'http://www.nexthope.net',
    'author': 'NextHope',
    'data': [
        'views/gestion_assurance_view.xml',				
    ],
    'demo': [],
    'auto_install': False,
    'installable': True,
}
