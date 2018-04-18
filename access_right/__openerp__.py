# -*- coding: utf-8 -*-

{
    "name": 'Access Right',
    "version": "1.0",
    "depends": [
        'base',
        'account',
        'account_financial_report_webkit',
        'account_voucher',
        'product',
        'commission',
        'account_journal_agency',
    ],
    "author": "Rakotomalala Haritiana Maminiaina",
    "category": "ARO",
    "installable": True,
    "data": [
        'res_groups_records.xml',
        'ir_model_access_records.xml',
        'ir_rule_records.xml',
        'security/commission_security.xml',
    ],
}
