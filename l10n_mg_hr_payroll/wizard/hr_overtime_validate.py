# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time

from openerp.osv import fields, osv
# import netsvc
# import pooler
from openerp.osv.orm import browse_record, browse_null
from openerp.tools.translate import _

class hr_employee_overtime_validate(osv.TransientModel):
    _name = "hr.employee.overtime.validate"
    _description = "Validation Heures Supplementaires"

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        """
         Changes the view dynamically
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param context: A standard dictionary
         @return: New arch of view.
        """
        if context is None:
            context = {}
        res = super(hr_employee_overtime_validate, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=False)
        return res

    def validate_planning(self, cr, uid, ids, context=None):
        """
        """
        planning_obj = self.pool.get('hr.employee.overtime')
        planning_obj.write(cr, uid, context['active_ids'], {'state':'valid'})
        return {}
    def cancel_planning(self, cr, uid, ids, context=None):
        """
        """
        planning_obj = self.pool.get('hr.employee.overtime')
        planning_obj.write(cr, uid, context['active_ids'], {'state':'refuse'})
        return {}
hr_employee_overtime_validate()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
