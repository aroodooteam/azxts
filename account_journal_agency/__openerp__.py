# -*- coding: utf-8 -*-

{
    "name": 'Account journal agency',
    "description": u"""
        Ajout de notion d´agence dans les journaux
    """,
    "version": "0.1",
    "depends": [
        'account',
        'base',
        'hr',
        'l10n_mg_aro',
    ],
    "author": "Rakotomalala Haritiana <haryoran04@gmail.com>",
    "category": "ARO",
    "installable": True,
    "data": [
        'security/ir.model.access.csv',
        'data/base_agency_data.xml',
        'data/account_account_templates.xml',
        'views/account_move_line_views.xml',
        'views/hr_employee_views.xml',
        'views/res_users_views.xml',
        'views/account_journal_agency_views.xml',
        'views/base_agency_views.xml',
        'views/account_entries_report_views.xml',
        'data/ir_sequence_records.xml',
        'data/l10n_mg_aro_journal.xml',
        'data/account_journal_data.xml',
        'data/account_journal_records.xml',
        'security/journal_security.xml',
    ],
}
