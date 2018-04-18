# -*- coding: utf-8 -*-

from openerp.osv import osv, fields
import time
from datetime import date, datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from openerp.tools.translate import _
import logging

_logger = logging.getLogger(__name__)

class stock_picking(osv.osv):

    _inherit = 'stock.picking'

    _columns = {
    'department_id' : fields.many2one("hr.department", string="Département"),
    'request_id' : fields.many2one("hr.consumable.request", string="Demande")
    }

class consumable_type(osv.osv):

    _name = 'consumable.type'

    _columns = {
    'name' : fields.char(string="Type"),
    'picking_type_id': fields.many2one('stock.picking.type', 'Emplacement', domain="[('code','=','outgoing')]"),
    }

class hr_consumable_request(osv.osv):
    """Demandes de Matériel.

    .. moduleauthor:: Geerish Sumbojee <geerish@omerp.net>

    """
    _name = "hr.consumable.request"
    _description = "Demande de materiel/consommables"
    
    def create(self, cr, uid, vals, context=None):
        if vals.get('name', '/') == '/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'hr.consumable.request') or '/'
        return super(hr_consumable_request, self).create(cr, uid, vals, context=context)
        
    def _employee_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)
        if ids:
            return ids[0]
        return False  
    
    def _department_get(self, cr, uid, context=None):
        ids = self.pool.get('hr.employee').search(cr, uid, [('user_id', '=', uid)], context=context)        
        ids = self.pool.get('hr.department').search(cr, uid, [('member_ids', '=', ids)], context=context)
        if ids:
            return ids[0]
        return False
    
    def _get_uom_id(self, cr, uid, *args):
        try:
            proxy = self.pool.get('ir.model.data')
            result = proxy.get_object_reference(cr, uid, 'product', 'product_uom_unit')
            return result[1]
        except Exception, ex:
            return False  

    _columns = {
        'name':fields.char('Numéro de demande', size=64),
        'note':fields.text('Note'),
        'date':fields.datetime('Date de demande'),
        'date_validate':fields.datetime('Date de validation'),
        'date_validate2':fields.datetime('Date 2eme validation'),
	    'employee_id':fields.many2one('hr.employee', 'Employe', readonly=True, required=True, states={'draft': [('readonly', False)], }),
        'department_id':fields.many2one('hr.department', 'Department', readonly=True, required=True, states={'draft': [('readonly', False)], }),
        'valid_user_id_1':fields.many2one('res.users', 'Autorisation'),
        'valid_user_id_2':fields.many2one('res.users', 'Validation'),
        'request_line': fields.one2many('hr.consumable.request.line', 'request_id', 'Ligne de requete', states={'draft': [('readonly', False)], 'done':[('readonly', True)]}, copy=False),
        'picking_id' : fields.many2one('stock.picking', 'Bon de livraison'),
        'type_id' : fields.many2one('consumable.type', 'Type'),
        'state':fields.selection([
            ('draft', 'Brouillon'),
            ('auth', 'Confirmé'),
            ('valid', 'Validé'),
            ('done', 'Terminé'),
            ('cancel', 'Annulé'),
            ],
            'Etat', readonly=True),
        }
    _defaults = {
        'product_uom' : _get_uom_id,
        'quantity': 1,
        'date': time.strftime(DEFAULT_SERVER_DATE_FORMAT),
        'state': 'draft',
        'employee_id':_employee_get,
        'department_id':_department_get,
        'name': lambda obj, cr, uid, context: '/',
		}
    _order = 'name desc'

    def create_picking(self, cr, uid, ids, context=None):
        """Create a picking for each order and validate it."""
        picking_obj = self.pool.get('stock.picking')
        partner_obj = self.pool.get('res.partner')
        move_obj = self.pool.get('stock.move')

        for order in self.browse(cr, uid, ids, context=context):
            picking_id = False
            picking_id = picking_obj.create(cr, uid, {
                'company_id':1,
                'origin': order.name,
                'partner_id': False,
                'date_done' : order.date,
                'move_type': 'direct',
                'note': order.note or "",
                'picking_type_id': order.type_id.picking_type_id.id,
                'invoice_state': 'none',
                'department_id':order.department_id.id
            }, context=context)
            self.write(cr, uid, [order.id], {'picking_id': picking_id}, context=context)
            pick = picking_obj.browse(cr, uid, [picking_id])
            for p in pick:
                picking_type = p.picking_type_id
                location_id = p.picking_type_id.default_location_src_id.id
            if order.employee_id.address_home_id:
                destination_id = order.employee_id.address_home_id.property_stock_customer.id
            elif picking_type:
                if not picking_type.default_location_dest_id:
                    raise osv.except_osv(_('Error!'), _('Missing source or destination location for picking type %s. Please configure those fields and try again.' % (picking_type.name,)))
                destination_id = picking_type.default_location_dest_id.id
            else:
                destination_id = partner_obj.default_get(cr, uid, ['property_stock_customer'], context=context)['property_stock_customer']

            move_list = []
            for line in order.request_line:
                if line.product_id and line.product_id.type == 'service':
                    continue

                move_list.append(move_obj.create(cr, uid, {
                    'name': line.name,
                    'product_uom': line.product_id.uom_id.id,
                    'product_uos': line.product_id.uom_id.id,
                    'picking_id': picking_id,
                    'product_id': line.product_id.id,
                    'product_uos_qty': abs(line.quantity),
                    'product_uom_qty': abs(line.quantity),
                    'state': 'draft',
                    'location_id': location_id if line.quantity >= 0 else destination_id,
                    'location_dest_id': destination_id if line.quantity >= 0 else location_id,
                }, context=context))
                
            if picking_id:
                picking_obj.action_confirm(cr, uid, [picking_id], context=context)
                picking_obj.action_assign(cr, uid, [picking_id], context=context)
            elif move_list:
                move_obj.action_confirm(cr, uid, move_list, context=context)
                move_obj.action_assign(cr, uid, move_list, context=context)
                # move_obj.action_done(cr, uid, move_list, context=context)
        return True

    def auth(self, cr, uid, ids, context=None):
        for req in self.browse(cr, uid, ids):
            if req.employee_id.user_id.id == uid and not self.pool['res.users'].has_group(cr, uid, 'base.group_direction'):
                raise osv.except_osv(_('Vous n\'avez pas l\'autorité de valider votre propre demande.\n'), _(
                        'Votre demande doit etre validée par votre chef hiérarchique.'))        
        product_obj = self.pool.get('product.product')
        stock_quant_obj = self.pool.get('stock.quant')         
        product_browse = self.browse(cr, uid, ids, context=context)
        stock_product_change = self.pool.get('stock.change.product.qty')
        request_line = product_browse.request_line
        for pl in request_line:
            qty = 0
            qty_give = pl.quantity
            product_id = pl.product_id.id
            qty = pl.product_id.qty_available
            if qty >= qty_give:
                qty -= qty_give
            else:
                raise osv.except_osv(_('Sorry'), _('la quantite en stock est insuffisant'))
        
        picking = self.create_picking(cr, uid, ids)
        if picking:
            self.write(cr, uid, ids, {'state': 'auth', 'valid_user_id_1':uid, 'date_validate':time.strftime(DEFAULT_SERVER_DATE_FORMAT)}, context=context)
            return True
        else:
            return False
    
    def done(self, cr, uid, ids, context=None):
        for req in self.browse(cr, uid, ids):
            if req.employee_id.user_id.id != uid :
                raise osv.except_osv(_('Vous n\'avez pas l\'autorite de réceptionner.\n'), _(
                        'Votre demande doit etre receptionnee par %s.' % (req.employee_id.name,)))
        self.write(cr, uid, ids, {'state': 'done'}, context=context)
        return True

    def cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'}, context=context)
        return True

    def refuse(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'refuse'}, context=context)
        return True

    def valid(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('stock.picking')        
        for picking in self.browse(cr, uid, ids):
            picking_obj.action_done(cr, uid, [picking.picking_id.id], context=context)
            self.write(cr, uid, ids, {'state': 'valid', 'valid_user_id_2':uid, 'date_validate2':time.strftime(DEFAULT_SERVER_DATE_FORMAT)}, context=context)
            return True
        else:
            return False
    

class hr_consumable_request_line(osv.osv):

    _name = "hr.consumable.request.line"
    _description = "Ligne de demande"
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Article', domain=[('medicament', '=', False), ('type', '=', 'product'), ('purchase_ok', '=', True)], change_default=True),
        'name':fields.char('Description', size=64),
        'quantity':fields.float('Quantité'),
        'uom_id': fields.many2one('product.uom', 'Unit de mesure ', required=True, readonly=False, states={'draft': [('readonly', False)]}),
        'request_id':fields.many2one('hr.consumable.request', 'Requete'),
        }    

    def product_id_change(self, cr, uid, ids, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang', False)

        warning = False
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product)

        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id])[0][1]
            if product_obj.description_sale:
                result['name'] += '\n' + product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['uom_id'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom:  # only happens if uom is False
            result['uom_id'] = product_obj.uom_id and product_obj.uom_id.id
            result['quantity'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight

        if not uom2:
            uom2 = product_obj.uom_id
        if qty > product_obj.qty_available:
            result['quantity'] = product_obj.qty_available
            warning_msgs = 'Attention seulement ' + str(product_obj.qty_available) + ' disponible'
        if warning_msgs:
            warning = {
                       'title': _('Erreur!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}
