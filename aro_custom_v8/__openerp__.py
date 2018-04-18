# -*- coding: utf-8 -*-

{
    "name": 'ARO Assurance Customisations',
    "description": u"""Module pour les besoins de ARO""",
    "version": "1.0",
    "depends": [
        'base',
        'account',
        'account_invoice_inherit',
        'account_journal_agency',
        'hr',
        'hr_holidays',
        'product',
        'sale',
    ],
    "author": "OpenMind Ltd",
    "category": "Departement",
    "installable": True,
    "data": [
        'security/ir.model.access.csv',
        'views/res_partner.xml',
        'views/account_move_line_view.xml',
        'views/product_category_view.xml',
        'views/product_template_view.xml',
        'views/res_apporteur_views.xml',
        'data/under_agency_data.xml',
        'data/product_category_data.xml',
        'data/product_template_data.xml',
    ],
}
