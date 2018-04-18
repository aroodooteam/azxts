# -*- coding: utf-8 -*-
from openerp.osv import fields, osv

class aro_payment(osv.osv):

    _name = "aro_payment"
    _description = "Mode de payement ARO"

    _columns = {
        'code':fields.char('Code', size=8),
        'name':fields.char('Type', size=64),
        'ref':fields.char('Reference', size=64),
        }

aro_payment()
