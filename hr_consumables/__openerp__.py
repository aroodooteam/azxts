{
    'name': 'HR consumables',
    'version': '1.0',
    'category': 'HR',
    'description': """
Gestion des consommables.
=========================

Test
""",
    'author': 'Geerish Sumbojee',
    'website': 'www.omerp.net',
    'license': 'AGPL-3',
    "depends" : ['base', 'hr', 'purchase'],
    "init_xml" : [],
    "update_xml" : ['hr.xml', 'sequence.xml', 'security/hr_consumables.xml'],
    "demo_xml" : [],
    "active": False,
    "installable": True
}
