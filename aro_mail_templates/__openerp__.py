# -*- coding: utf-8 -*-

{
    "name": "Aro mail templates",
    "version": "0.1",
    "author": "aroodoo_asus_hary",
    "category": "Tools",
    "complexity": "normal",
    "data": [
        "data/auth_signup_data.xml", # un comment to enable js, css code
        # "security/security.xml",
        # "security/ir.model.access.csv",
        # "views/view.xml",
        # "actions/act_window.xml",
        # "menu.xml",
        # "data/data.xml",
    ],
    "depends": [
        "base",
        "auth_signup",
    ],
    "qweb": [
        # "static/src/xml/*.xml",
    ],
    "test": [
    ],
    "installable": True,
    "auto_install": False,
}
