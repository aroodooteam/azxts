# -*- coding:utf-8 -*-

import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
from openerp.tools.safe_eval import safe_eval as eval

class hr_medical(osv.osv):

    _name = "hr.medical"
    _description = "Human Ressources Medical"

    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.medical') or '/'
        return super(hr_medical, self).create(cr, uid, vals, context=context)

    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False

    def open(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'open'}, context=context)
        return True

    def done(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def livrer(self, cr, uid, ids, context=None):
        product_obj = self.pool.get('product.product')
        stock_quant_obj = self.pool.get('stock.quant')
        product_browse = self.browse(cr, uid, ids, context=context)
        stock_product_change = self.pool.get('stock.change.product.qty')
        prescription_line = product_browse.prescription_line
        for pl in prescription_line:
            qty = 0
            qty_give = pl.product_uom_qty
            product_id = pl.product_id.id
            sq_ids = stock_quant_obj.search(cr, uid, [('product_id', '=', product_id)])
            if sq_ids != []:
                stock_quant_obj_browse = stock_quant_obj.browse(cr, uid, sq_ids)
                qty = stock_quant_obj_browse.qty
                if qty >= qty_give:
                    qty -= qty_give
                else:
                    raise osv.except_osv(_('Sorry'), _('la quantite en stock est insuffisant'))
            else:
                raise osv.except_osv(_('Sorry'), _('ce produit est indisponible'))

            l = {'qty':qty}
            res = stock_quant_obj.write(cr, uid, sq_ids, l)

        self.write(cr, uid, ids, {'state': 'livrer'}, context=context)

        return True

    _columns = {
        'name':fields.char('Numero', size=64),
        'employee_id':fields.many2one('hr.employee', 'Employe', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'user_id':fields.many2one('res.users', 'Medecin'),
        'date':fields.date('Date', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'diagnostique':fields.text('Diagnostique', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}),
        'prescription_line': fields.one2many('prescription.line', 'medical_id', 'Prescription', states={'draft': [('readonly', False)], 'done':[('readonly', True)]}, copy=False),
        'name': fields.text('Description', required=False, readonly=False, states={'draft': [('readonly', False)]}),
        'product_id': fields.many2one('product.product', 'Medicament', domain=[('medicament', '=', True)], change_default=True),
        # 'product_uom_qty': fields.float('Quantite', required=True, readonly=False, states={'draft': [('readonly', False)]}),
        # 'product_uom': fields.many2one('product.uom', 'Unit de mesure ', required=True, readonly=False, states={'draft': [('readonly', False)]}),
        'state':fields.selection([
            ('draft', 'Brouillon'),
            ('open', 'Ouverte'),
            ('cancel', 'Annule'),
            ('livrer', 'Livrer'),
            ('done', 'Terminer'),
            ],
            'Etat', readonly=True),
        }
    _defaults = {
        # 'product_uom' : _get_uom_id,
        # 'product_uom_qty': 1,
        'date': fields.date.context_today,
        'state': 'draft',
        'user_id': lambda obj, cr, uid, context: uid,
        'name': lambda obj, cr, uid, context: '/',
    	}

hr_medical()

class prescription_line(osv.osv):

    _name = "prescription.line"
    _description = "Ligne de Prescription"

    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False

    _columns = {
        'medical_id': fields.many2one('hr.medical', 'Prescription', required=True, ondelete='cascade', select=True),
        'name': fields.text('Description', required=True, readonly=False),  # , states={'draft': [('readonly', False)]}
        'product_id': fields.many2one('product.product', 'Medicament', domain=[('medicament', '=', True)], change_default=True),
        'product_uom_qty': fields.float('Quantite', required=True, readonly=False, states={'draft': [('readonly', False)]}),
        'product_uom': fields.many2one('product.uom', 'Unit de mesure ', required=True, readonly=False, states={'draft': [('readonly', False)]}),  # , states={'draft': [('readonly', False)]}
        'state':fields.selection([
            ('draft', 'Brouillon'),
            ('open', 'Ouverte'),
            ('cancel', 'Annule'),
            ('livrer', 'Livrer'),
            ('done', 'Terminer'),
            ],
            'Etat', readonly=True),

        }

    _defaults = {
        'product_uom' : _get_uom_id,
        'product_uom_qty': 1,
        'state':'draft',
    }

    def product_id_change(self, cr, uid, ids, product, qty=0, uom=False, name='', update_tax=True, context=None):
        context = context or {}
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        product_obj = self.pool.get('product.product')

        if not product:
            return {'value': {
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   }}

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False

        if (not uom):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos_qty'] = qty
                uos_category_id = False
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                    }

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price
        return {'value': result, 'domain': domain, 'warning': warning}


prescription_line()

class product_template(osv.osv):
    _inherit = 'product.template'

    def _get_buy_route(self, cr, uid, context=None):

        buy_route = self.pool.get('ir.model.data').xmlid_to_res_id(cr, uid, 'medicament.route_warehouse0_buy')
        if buy_route:
            return [buy_route]
        return []

    _columns = {
        'medicament': fields.boolean('Medicament', help='Check if the product is a medicament'),

        }

product_template()
