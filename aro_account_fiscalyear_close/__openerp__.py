# -*- coding: utf-8 -*-

{
    "name": "ARO ACCOUNT_FISCALYEAR_CLOSE WIZARD",
    "version": "0.1",
    "author": "Rakotomalala Haritiana Maminiaina <haryoran04@gmail.com>",
    "category": "Tools",
    "complexity": "normal",
    "data": [
        # "data/templates.xml", # un comment to enable js, css code
        # "security/security.xml",
        # "security/ir.model.access.csv",
        "views/aro_account_fiscalyear_close_view.xml",
        "views/restricted_account_agency_view.xml",
        "views/base_agency_view.xml",
        # "menu.xml",
        # "data/data.xml",
    ],
    "depends": [
        "base",
        "account",
        "account_journal_agency"
    ],
    "installable": True,
    "auto_install": False,
}
