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
# Generated by the OpenERP plugin for Dia !
# from osv import fields
import datetime
from openerp import models, api, fields, tools, _

from openerp.exceptions import Warning
import logging

_logger = logging.getLogger(__name__)


class hr_employee(models.Model):
    _inherit = 'hr.employee'
    manager_user_id = fields.Many2one('res.users', related='parent_id.user_id')


class hr_holidays_status_type(models.Model):

    _name = "hr.holidays.status.type"
    _description = 'Type de permission'
    name = fields.Char('Type de permission')
    limit = fields.Float('Limite')
    proof = fields.Char('Justificatif')


class hr_replacement(models.Model):

    _name = 'hr.replacement'

    employee_id = fields.Many2one(string=u'Remplaçant',
                                  comodel_name='hr.employee')
    name = fields.Many2one(string=u'Congé', comodel_name='hr.holidays')
    date_start = fields.Datetime('Debut')
    date_stop = fields.Datetime('Fin')
    replace_employee_id = fields.Many2one('hr.employee',
                                          related='name.employee_id')
    replace_department_id = fields.Many2one(
        'hr.department', related='replace_employee_id.department_id')


class hr_holidays_status(models.Model):

    _inherit = "hr.holidays.status"

    @api.multi
    def get_days(self, employee_id, context=None):
        result = dict((holiday.id,
                       dict(max_leaves=0, leaves_taken=0, remaining_leaves=0,
                            virtual_remaining_leaves=0)) for holiday in self)
        ids = []
        for holiday in self:
            ids.append(holiday.id)
        holiday_ids = self.env['hr.holidays'].search(
            [('employee_id', '=', employee_id),
             ('state', 'in', ['confirm', 'validate1', 'validate']),
             ('holiday_status_id', 'in', ids)])
        accounted = []
        for holiday in holiday_ids:
            status_dict = result[holiday.holiday_status_id.id]
            nb_dtmp = holiday.number_of_days_temp
            if holiday.type == 'add':
                status_dict['virtual_remaining_leaves'] += nb_dtmp
                if holiday.state == 'validate':
                    status_dict['max_leaves'] += nb_dtmp
                    status_dict['remaining_leaves'] += nb_dtmp
            elif holiday.type == 'remove':  # number of days is negative
                status_dict['virtual_remaining_leaves'] -= nb_dtmp
                if holiday.state == 'validate':
                    status_dict['leaves_taken'] += holiday.number_of_days_temp
                    status_dict['remaining_leaves'] -= nb_dtmp
            if holiday.holiday_status_id.id not in accounted and \
               holiday.holiday_status_id.anciennete:
                accounted.append(holiday.holiday_status_id.id)
                employee = self.env['hr.employee'].search(
                    [('id', '=', employee_id)])
                seniority = employee.seniority.split(' ')
                if ('mois,') in seniority:
                    seniority.remove('mois,')
                if ('jours') in seniority:
                    seniority.remove('jours')
                if ('ans,') in seniority:
                    seniority.remove('ans,')
                months = int(seniority[1])
                to_exclude = 0
                for hol in employee.job_id.hr_holiday_job_ids:
                    if hol.name == holiday.holiday_status_id:
                        to_exclude = hol.days * months
                status_dict['max_leaves'] -= to_exclude
        return result

    weekend = fields.Boolean('Ouvrable')
    days = fields.Float('Jours à attribuer')
    frequency = fields.Selection(
        [('monthly', 'Mensuel'), ('yearly', 'Annuel')], 'Attribution')
    reset = fields.Boolean(u'Reinitialisation annuel')
    global_holiday = fields.Boolean(
        u'Congé commun', help='Definition pas necessaire dans le poste')
    anciennete = fields.Boolean(u'Attribution sur ancienneté')


class hr_holidays(models.Model):

    _inherit = "hr.holidays"

    @api.multi
    def get_if_manager(self):
        uid = self.env.user.id
        emp_obj = self.env['hr.employee']
        employee = emp_obj.search([('user_id', '=', uid)])
        for emp in employee:
            if emp.manager:
                return emp.manager
            else:
                return False

    available_holidays = fields.Float('Jours diponible')
    status_type_id = fields.Many2one(
        'hr.holidays.status.type', 'Type de permission')
    replacement = fields.Boolean(string='Remplacement à pourvoir',
                                 related='employee_id.job_id.replacement')
    replacement_ids = fields.One2many(
        string='Remplacement', comodel_name='hr.replacement',
        inverse_name='name')
    manager = fields.Boolean(string='Field label', default=get_if_manager)

    @api.one
    def holidays_first_validate(self):
        if self.employee_id.user_id == self.env.user.id:
            raise Warning(
                _(u'''Vous n'avez pas l'autorité de valider ce congés.\n
                  Contactez le département des Ressources Humaines.'''))
        if self.employee_id.parent_id.user_id.id == self.env.user.id:
            return super(hr_holidays, self).holidays_first_validate()
        elif self.env['res.users'].has_group('base.group_hr_user'):
            return super(hr_holidays, self).holidays_first_validate()
        elif self.env['res.users'].has_group('base.group_hr_manager'):
            return super(hr_holidays, self).holidays_first_validate()
        else:
            raise Warning(
                _(u'''Vous n'avez pas l'autorité de valider ce congé.\n
                  Contactez le département des Ressources Humaines.'''))

    @api.one
    def holidays_validate(self):
        if self.employee_id.user_id == self.env.user.id:
            raise Warning(
                _(u'''Vous n'avez pas l'autorité de valider ce congés.\n
                  Contactez le département des Ressources Humaines.'''))
        if self.employee_id.parent_id.parent_id.user_id.id == self.env.user.id:
            return super(hr_holidays, self).holidays_first_validate()
        elif self.env.user.has_group('base.group_hr_user'):
            return super(hr_holidays, self).holidays_first_validate()
        elif self.env.user.has_group('base.group_hr_manager'):
            return super(hr_holidays, self).holidays_first_validate()
        elif self.employee_id.parent_id.parent_id.user_id.has_group('base.group_hr_user') or self.employee_id.parent_id.parent_id.user_id.has_group('base.group_hr_manager'):
            return super(hr_holidays, self).holidays_first_validate()
        else:
            raise Warning(
                _(u'''Vous n'avez pas l'autorité de valider ce congés.\n
                  Contactez le département des Ressources Humaines.'''))

    @api.onchange('number_of_days_temp')
    def onchange_days(self):
        if self.type == 'add':
            return False
        if not self.date_from:
            return False
        date_from = datetime.datetime.strptime(
            self.date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT)
        hour_from = date_from.timetuple()[3]
        weekend = False  # ouvrable
        if self.employee_id.job_id.hr_holiday_job_ids:
            for holiday in self.employee_id.job_id.hr_holiday_job_ids:
                if holiday.name == self.holiday_status_id:
                    if holiday.weekend:
                        weekend = True
        else:
            if self.holiday_status_id.weekend:
                weekend = True

        if weekend:
            if self.number_of_days_temp % 1 > 0:
                days = int(self.number_of_days_temp)
                hours = int(8 * (self.number_of_days_temp % 1))
                if days == 0:
                    hours -= 0
            elif int(self.number_of_days_temp) == 1:
                days = 0
                if hour_from > 8:
                    hours = 23
                else:
                    hours = 9 - 1
            else:
                days = int(self.number_of_days_temp) - 1
                if hour_from > 8:
                    hours = 23
                else:
                    hours = 9 - 1
            temp_days = 0
            date_to = datetime.datetime.strptime(
                self.date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            public_holidays = []
            hhpl = self.env['hr.holidays.public.line']
            hhpl_doms = [('date', '>=', self.date_from)]
            for public_holiday in hhpl.search(hhpl_doms):
                public_holidays.append(
                    datetime.datetime.strptime(
                        public_holiday.date,
                        tools.DEFAULT_SERVER_DATE_FORMAT).replace(
                            hour=hour_from, minute=0))

            while temp_days < days:
                date_to = date_to + datetime.timedelta(days=1)
                while date_to.isoweekday() >= 6:
                    date_to = date_to + datetime.timedelta(days=1)
                    _logger.info(date_to)

                if date_to.isoweekday() < 6:
                    if date_to in public_holidays:
                        _logger.info(date_to in public_holidays)
                        date_to = date_to + datetime.timedelta(days=1)
                        while date_to.isoweekday() >= 6:
                            date_to = date_to + datetime.timedelta(days=1)
                temp_days += 1
            date_to = date_to + datetime.timedelta(hours=hours)
            self.date_to = date_to
        else:
            if self.status_type_id:
                if self.status_type_id.limit < self.number_of_days_temp:
                    self.number_of_days_temp = self.status_type_id.limit
            days = self.number_of_days_temp
            hours = 0
            if self.number_of_days_temp % 1 > 0:
                days = int(self.number_of_days_temp)
                hours = int(8 * (self.number_of_days_temp % 1))
                if days == 0:
                    hours -= 0
            elif int(self.number_of_days_temp) == 1:
                days = 0
                if hour_from > 8:
                    hours = 23
                else:
                    hours = 9 - 1
            else:
                days = int(self.number_of_days_temp) - 1
                if hour_from > 8:
                    hours = 23
                else:
                    hours = 9 - 1
            # if self.number_of_days_temp<1:
            #    self.number_of_days_temp=1
            dt_from = datetime.datetime.strptime(
                self.date_from, tools.DEFAULT_SERVER_DATETIME_FORMAT)
            self.date_to = dt_from + datetime.timedelta(days=days, hours=hours)

    # @api.onchange('holiday_status_id')
    def onchange_status(self):
        if not 'holiday_status_id':
            return False
        hhs_obj = self.env['hr.holidays.status']
        if self.holiday_type != 'employee' or self.type != 'remove' \
           or not self.employee_id or self.holiday_status_id.limit:
            self.available_holidays = 0
        else:
            leave_days = hhs_obj.get_days(
                self.employee_id.id, context=None)[self.holiday_status_id.id]
            self.available_holidays = leave_days['virtual_remaining_leaves']


# reactivate this class when need payroll or move it
# in another module
"""
class hr_payroll_ma(models.Model):
    _inherit = 'hr.payroll_ma'

    attribution = fields.Boolean('Attribution')

    @api.one
    def set_holidays(self):
        # employee_obj = self.env['hr.employee']
        holiday_obj = self.env['hr.holidays']
        holiday_status_obj = self.env['hr.holidays.status']
        global_holidays = holiday_status_obj.search(
            [('global_holiday', '=', True)])
        # employees = employee_obj.search([('active', '=', True)])

        for bulletin in self.bulletin_line_ids:
            employee = bulletin.employee_id
            days_worked = bulletin.working_days
            p_name = self.period_id.name
            for holiday in employee.job_id.hr_holiday_job_ids:
                if holiday.name.frequency == 'monthly':
                    dt_stop = datetime.datetime.strptime(
                        self.period_id.date_stop, '%Y-%m-%d')
                    dt_start = datetime.datetime.strptime(
                        self.period_id.date_start, '%Y-%m-%d')
                    days_in_month = dt_stop - dt_start
                    ratio = days_worked / (days_in_month.days + 1)
                    attribution = ratio * holiday.days
                    data = {
                        'name': u'Attribution congé : ' + p_name,
                        'employee_id': employee.id,
                        'holiday_status_id': holiday.name.id,
                        'number_of_days_temp': attribution,
                        'holiday_type': 'employee',
                        'type': 'add',
                    }
                    new_holiday = holiday_obj.create(data)
                    new_holiday.signal_workflow('validate')
                    new_holiday.signal_workflow('second_validate')
                elif holiday.name.frequency == 'yearly':
                    if self.period_id.name[:2] == '12':
                        leave_days = holiday.get_days(
                            employee.id, context=None)[holiday.id]
                        available_holidays = leave_days['virtual_remaining_leaves']
                        if holiday.reset and available_holidays > 0:
                            data = {
                                'name': u'Reinitialisation congé : ' + p_name,
                                'employee_id': employee.id,
                                'holiday_status_id': holiday.name.id,
                                'number_of_days_temp': -available_holidays,
                                'holiday_type': 'employee',
                                'type': 'add',
                            }
                            new_holiday = holiday_obj.create(data)
                            new_holiday.signal_workflow('validate')
                            new_holiday.signal_workflow('second_validate')
                        data = {
                            'name': u'Attribution congé : ' + p_name,
                            'employee_id': employee.id,
                            'holiday_status_id': holiday.name.id,
                            'number_of_days_temp': holiday.days,
                            'holiday_type': 'employee',
                            'type': 'add',
                        }
                        new_holiday = holiday_obj.create(data)
                        new_holiday.signal_workflow('validate')
                        new_holiday.signal_workflow('second_validate')
            for holiday in global_holidays:
                if holiday.frequency == 'monthly':
                    dt_stop = datetime.datetime.strptime(
                        self.period_id.date_stop, '%Y-%m-%d')
                    dt_start = datetime.datetime.strptime(
                        self.period_id.date_start, '%Y-%m-%d')
                    days_in_month = dt_stop - dt_start
                    ratio = days_worked / (days_in_month.days + 1)
                    attribution = ratio * holiday.days
                    _logger.info(employee.name)
                    _logger.info(days_worked)
                    _logger.info(days_in_month.days)
                    _logger.info(attribution)
                    data = {
                        'name': u'Attribution congé : ' + p_name,
                        'employee_id': employee.id,
                        'holiday_status_id': holiday.id,
                        'number_of_days_temp': attribution,
                        'holiday_type': 'employee',
                        'type': 'add',
                    }
                    new_holiday = holiday_obj.create(data)
                    new_holiday.signal_workflow('validate')
                    new_holiday.signal_workflow('second_validate')
                elif holiday.frequency == 'yearly':
                    if self.period_id.name[:2] == '12':
                        leave_days = holiday.get_days(
                            employee.id, context=None)[holiday.id]
                        available_holidays = leave_days['virtual_remaining_leaves']

                        if holiday.reset and available_holidays > 0:
                            data = {
                                'name': u'Reinitialisation congé : ' + p_name,
                                'employee_id': employee.id,
                                'holiday_status_id': holiday.id,
                                'date_from': self.period_id.date_stop,
                                'date_to': self.period_id.date_stop,
                                'number_of_days_temp': available_holidays,
                                'holiday_type': 'employee',
                                'type': 'remove',
                            }
                            new_holiday = holiday_obj.create(data)
                            new_holiday.signal_workflow('validate')
                            new_holiday.signal_workflow('second_validate')
                        data = {
                            'name': u'Attribution congé : ' + p_name,
                            'employee_id': employee.id,
                            'holiday_status_id': holiday.id,
                            'number_of_days_temp': holiday.days,
                            'holiday_type': 'employee',
                            'type': 'add',
                        }
                        new_holiday = holiday_obj.create(data)
                        new_holiday.signal_workflow('validate')
                        new_holiday.signal_workflow('second_validate')

        self.attribution = True
"""
