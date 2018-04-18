# -*- coding: utf-8 -*-

{
    "name": 'Commissions - Client final module - ARO',
    "description": u"""
Commissions - Client final module - ARO
===========================================
**Credits:** NextHope.
""",
    "version": "1.0",
    "depends": [
        'base',
        'account',
    ],
    "author": "NextHope",
    "category": "ARO Custom",
    "installable": True,
    "data": [
        'security/ir.model.access.csv',
        'views/commission_view.xml',
        'views/account_invoice_view.xml',
        'views/ir_actions_act_window_records.xml',
        'views/ir_ui_menu_records.xml',
    ],
}
