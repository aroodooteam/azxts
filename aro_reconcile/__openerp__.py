# -*- coding: utf-8 -*-

{
    "name": "ARO RECONCILE",
    "version": "0.1",
    "author": "Haritiana Rakotomalala",
    "category": "ARO",
    "complexity": "normal",
    "data": [
        # "data/templates.xml", # un comment to enable js, css code
        # "security/security.xml",
        # "security/ir.model.access.csv",
        "views/reconcile_widget.xml",
        "views/partner_group_wiz_view.xml",
        "views/res_partner_view.xml",
        "wizard/account_reconcile_view.xml",
        # "actions/act_window.xml",
        # "menu.xml",
        # "data/data.xml",
    ],
    "depends": [
        "base",
        "account",
        "web",
    ],
    "qweb":[
        "static/src/xml/account_move_reconciliation.xml",
    ],
    "installable": True,
    "auto_install": False,
}
