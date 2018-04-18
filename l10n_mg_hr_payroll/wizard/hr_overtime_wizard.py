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

class hr_employee_overtime_wiz(osv.TransientModel):
    _name = 'hr.employee.overtime.wiz'
    _description = 'Allocation dheures sup par employees'
    _columns = {
        'date': fields.date('Date', required=True),
        'hours': fields.float('Heures Alloué', required=True),
        'period_id': fields.many2one('account.period', 'Periode Salariale', required=True),
        'depts': fields.many2many('hr.department', 'summ_dept_rel', 'sum_id', 'dept_id', 'Department(s)'),
        'employee_ids': fields.many2many('hr.employee', 'summ_dept_emp_rel', 'sum_id', 'emp_id', 'Employee(s)'),
        'type' : fields.selection([('hs', 'Heures Supplementaires'), ('ferie', 'Ferie'), ('nuit', 'Nuit'), ('nuit_extra', 'Nuit Extra')], 'Type', required=True),
        }

    def _get_depts(self, cursor, user, context={}):
        employee = self.pool.get('hr.employee').search(cursor, user, [('user_id', '=', user)])
        dept_id = self.pool.get('hr.employee').browse(cursor, user, employee, context={})[0].department_id.id
        depts = self.pool.get('hr.department').search(cursor, user, [('parent_id', 'in' , [dept_id])])
        depts.append(dept_id)
        return depts

    def _get_employee(self, cursor, user, context={}):
        employee = self.pool.get('hr.employee').search(cursor, user, [('user_id', '=', user)])
        dept_id = self.pool.get('hr.employee').browse(cursor, user, employee, context={})[0].department_id.id
        depts = self.pool.get('hr.department').search(cursor, user, [('parent_id', 'in' , [dept_id])])
        depts.append(dept_id)
        return self.pool.get('hr.employee').search(cursor, user, [('department_id', 'in', depts)])

    def _from_date(self, cursor, user, context={}):
        return datetime.date.today().strftime('%Y-%m-%d');


    _defaults = {
         'date': _from_date,
         'depts': _get_depts,
         'employee_ids': _get_employee,
         'type':'hs',
        }

    def generate_leaves(self, cr, uid, ids, context=None):
        data = self.read(cr, uid, ids, [])[0]
        planning_obj = self.pool.get('hr.employee.overtime')
        if not data['employee_ids']:
            raise osv.except_osv(_('Error'), _('You have to select at least 1 Employee. And try again'))
        created = []
        st = datetime.datetime.strptime(data['date'], '%Y-%m-%d')
        for employee in data['employee_ids']:
            print data['period_id']
            print data['period_id'][0]
            print data['hours']
            print data['type']
            created.append(planning_obj.create(cr, uid, {'type':data['type'], 'name':employee, 'date':st, 'period_id':data['period_id'][0], 'hours':data['hours'], 'state':'draft'}))

        return {
            'domain': "[('id','in', [" + ','.join(map(str, created)) + "])]",
            'name': 'Planning',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'hr.employee.overtime',
            'view_id': False,
            'type': 'ir.actions.act_window',
        }


hr_employee_overtime_wiz()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
