# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011 OpenERP SA (<http://openerp.com>).
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
{
    'name': 'Malagasy Payroll',
    'category': 'Localization/Payroll',
    'author': 'Geerish Sumbojee (Open Mind Ltd)',
    'depends': [
        'base', 'hr', 'hr_contract',
        'account', 'hr_holidays',
        'hr_attendance', 'hr_recruitment',
    ],
    'version': '1.0',
    'sequence': 39,
    'description': """
Module Paie Malgache Assurance ARO.
===================================

    """,

    'active': False,
    'data': [
        # "hr_employee_assiduite_view.xml",
        # 'wizard/hr_overtime_wizard_view.xml',
        # 'views/hr_overtime_view.xml',
        # 'wizard/hr_contract_modify.xml',
        # 'wizard/hr_overtime_validate_view.xml',
        # 'views/loan_view.xml',        
        'views/hr_employee_sanction_view.xml',
        'views/hr_contract_view.xml',
        'views/hr_employee_view.xml',
        'views/children_view.xml',
        # 'views/config.xml',
        'views/hr_view.xml',
        # 'views/hr_payroll_ma_view.xml',
        # 'views/hr_payroll_ma_sequence.xml',
        # 'views/hr_payroll_ma_data.xml',
        # 'views/hr_payroll_ma_report.xml',
        # 'views/hr_payroll_ma_wizard.xml',
        # 'security/hr_payroll_ma_security.xml',
        'security/ir.model.access.csv',
        # 'security/ir_rule.xml',
        # 'report/reports.xml',
        # 'wizard/hr_cnaps_wizard_view.xml',
        # 'wizard/hr_advantage_modify.xml',
        'views/hr_holiday.xml',
        'views/hr_job.xml',
        'views/hr_qualification.xml',
        # 'views/hr_call.xml',
    ],
    'installable': True,
    'application': True,

}
