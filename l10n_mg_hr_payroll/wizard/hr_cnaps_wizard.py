# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    $Id: account.py 1005 2005-07-25 08:41:42Z nicoe $
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
import datetime
import calendar
from openerp.osv import osv, fields
from openerp.tools.translate import _

class hr_cnaps_wiz(osv.TransientModel):
    _name = 'hr.cnaps.wiz'
    _description = 'Rapport CNaPS Groupe'
    _columns = {
        'employee_ids': fields.many2many('hr.employee', 'cnaps_dept_emp_rel', 'sum_id', 'emp_id', 'Employee(s)'),
        }

    def check_report(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        data = {'ids':[]}
        for form in self.browse(cr, uid, ids):
            for employee in form.employee_ids:
                data['ids'].append(employee.id)
        return {'type': 'ir.actions.report.xml', 'report_name': 'hr.employee.groupedcnapsrequest', 'datas': data}

hr_cnaps_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
