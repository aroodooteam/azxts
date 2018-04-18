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

from openerp.osv import fields, osv
import datetime


class hr_employee_overtime(osv.osv):
    _name = 'hr.employee.overtime'

    def _wb(self, cr, uid, ids, field_name, arg, context):
        employees = self.read(cr, uid, ids, ['date_start', 'id'], context)
        res = {}
        for employee in employees:
            if employee['date_start']:
                res[employee['id']] = datetime.datetime.strptime(
                    employee['date_start'], '%Y-%m-%d %H:%M:%S').strftime('%W')
        return res

    def _hours(self, cr, uid, ids, field_name, arg, context):
        employees = self.read(cr, uid, ids,
                              ['date_start', 'date_stop', 'id'], context)
        res = {}
        for employee in employees:
            if employee['date_start'] and employee['date_start']:
                start = datetime.datetime.strptime(
                    employee['date_start'], '%Y-%m-%d %H:%M:%S')
                stop = datetime.datetime.strptime(
                    employee['date_stop'], '%Y-%m-%d %H:%M:%S')
                diff = stop - start
                diff = float(diff.seconds) / 3600
                res[employee['id']] = diff
            else:
                res[employee['id']] = 0
        return res

    _columns = {
        'name': fields.many2one('hr.employee', u'Salarié'),
        'department_id': fields.related(
            'name', 'department_id', type='many2one', relation='hr.department',
            string='Departement', store=True),
        'date_start': fields.datetime('Début HS'),
        'date_stop': fields.datetime('Fin HS'),
        'period_id': fields.many2one('account.period', 'Periode Salariale',
                                     required=True),
        'week': fields.function(_wb, method=True, string='Semaine',
                                store=True),
        'hours': fields.function(_hours, method=True,
                                 string='Heures Travaille en HS'),
        # 'hours':fields.float('Heures Travaille en HS'),
        'type': fields.selection(
            [('hs', 'Heures Supplementaires'), ('ferie', 'Ferie'),
             ('nuit', 'Nuit'), ('nuit_extra', 'Nuit Extra')],
            'Type', required=True),
        'state': fields.selection(
            [('draft', 'Draft'), ('valid', 'Valid'),
             ('cancel', 'Annule'), ('refuse', 'Refuse')],
            'State', readonly=True, required=True),
    }
    _defaults = {
        'state': 'draft'
    }


hr_employee_overtime()
