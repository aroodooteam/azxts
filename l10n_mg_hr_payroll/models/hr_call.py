# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP,  Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation,  either version 3 of the
#    License,  or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not,  see <http://www.gnu.org/licenses/>.
#
##############################################################################
# Generated by the OpenERP plugin for Dia !

# import datetime
from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class hr_call(models.Model):
    _name = 'hr.call'

    name = fields.Many2one(string=u'Employé', comodel_name='hr.employee')
    job_id = fields.Many2one('hr.job', related='name.job_id')
    work_location = fields.Char(related='name.work_location', store=True)
    date_start = fields.Datetime(string='Date Debut')
    date_stop = fields.Datetime(string='Date fin')