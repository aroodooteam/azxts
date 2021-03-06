# -*- encoding: utf-8 -*-
import time
import locale
import datetime
from report import report_sxw
import time
import pooler
import rml_parse
import mx.DateTime
from mx.DateTime import RelativeDateTime, now, DateTime, localtime

class journal_paie_report(rml_parse.rml_parse):
    
    def __init__(self, cr, uid, name, context):
        super(journal_paie_report, self).__init__(cr, uid, name, context)
        self.localcontext.update({
            'time': time,
            'get_period'  : self.get_period,
            'get_partner' : self.get_partner,
            'get_department' : self.get_department,
            'get_fiscalyear' : self.get_fiscalyear,
            'get_function' : self.get_function,
            'get_total':self.get_total,
            'get_journal' : self.get_journal,
            'get_cotisations' : self.get_cotisations,
            'get_comms' : self.get_comms,
            'get_base' : self.get_base,
            'get_base_total' : self.get_base_total,


#            'get_rappel':self.rappel,

        })
    
        
    def get_fiscalyear(self, fiscalyear_id):
        fiscalyear_obj = pooler.get_pool(self.cr.dbname).get('account.fiscalyear')
        return fiscalyear_obj.read(self.cr, self.uid, [fiscalyear_id], ['name'])[0]['name']
    
    def get_partner(self, partner_id):
        partner_obj = pooler.get_pool(self.cr.dbname).get('res.partner')
        return partner_obj.read(self.cr, self.uid, [partner_id], ['name'])[0]['name']

    def get_department(self, department_id):
        partner_obj = pooler.get_pool(self.cr.dbname).get('hr.department')
        return partner_obj.read(self.cr, self.uid, [department_id], ['name'])[0]['name']
    
    def get_period(self, period_id):
        period_obj = pooler.get_pool(self.cr.dbname).get('account.period')
        period = period_obj.read(self.cr, self.uid, [period_id])[0]
        return 'Periode du %s au %s' % (period['date_start'], period['date_stop'])
    
    def get_function(self, contract_id):
        contract = pooler.get_pool(self.cr.dbname).get('hr.contract')
	contracts = contract.browse(self.cr, self.uid, [contract_id])	
	for contract in contracts:
		return  contract.job_id.name
    def get_comms(self, matricule, period_id):
        bulletin = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin')
	employee = pooler.get_pool(self.cr.dbname).get('hr.employee')
        bulletin_line = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin.line')
	employee = employee.search(self.cr, self.uid, [('matricule', '=', matricule)])[0]
        bulletin = bulletin.search(self.cr, self.uid, [('period_id', '=', period_id), ('employee_id', '=', employee)])[0]
	bulletin_lines = bulletin_line.search(self.cr, self.uid, [('id_bulletin', '=', bulletin), ('name', 'in', ['g400 Commission sur vente', 'Prime divers', '3700 - Commissions sur Vente'])])
	bulletin_lines = bulletin_line.browse(self.cr, self.uid, bulletin_lines)
	amount = 0
	print bulletin_line
	for line in bulletin_lines:
		print line
		amount += line.subtotal_employee
	return amount

    def get_base(self, matricule, period_id):
        bulletin = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin')
        employee = pooler.get_pool(self.cr.dbname).get('hr.employee')
        bulletin_line = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin.line')
        employee = employee.search(self.cr, self.uid, [('matricule', '=', matricule)])[0]
        bulletin = bulletin.search(self.cr, self.uid, [('period_id', '=', period_id), ('employee_id', '=', employee)])[0]
        bulletin_lines = bulletin_line.search(self.cr, self.uid, [('id_bulletin', '=', bulletin), ('name', '=', 'Salaire de base')])
        bulletin_lines = bulletin_line.browse(self.cr, self.uid, bulletin_lines)
        amount = 0
        for line in bulletin_lines:
                return line.subtotal_employee
    def get_base_total(self, period_id):
        bulletin = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin')
        employee = pooler.get_pool(self.cr.dbname).get('hr.employee')
        bulletin_line = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin.line')
        bulletin = bulletin.search(self.cr, self.uid, [('period_id', '=', period_id)])
        bulletin_lines = bulletin_line.search(self.cr, self.uid, [('id_bulletin', 'in', bulletin), ('name', '=', 'Salaire de base')])
        bulletin_lines = bulletin_line.browse(self.cr, self.uid, bulletin_lines)
        amount = 0
        for line in bulletin_lines:
                amount += line.subtotal_employee
        return amount

    def get_cotisations(self, matricule, period_id):
        bulletin = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin')
        employee = pooler.get_pool(self.cr.dbname).get('hr.employee')
        bulletin_line = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin.line')
        employee = employee.search(self.cr, self.uid, [('matricule', '=', matricule)])[0]
        bulletin = bulletin.search(self.cr, self.uid, [('period_id', '=', period_id), ('employee_id', '=', employee)])[0]
        bulletin_lines = bulletin_line.search(self.cr, self.uid, [('id_bulletin', '=', bulletin)])
        bulletin_lines = bulletin_line.read(self.cr, self.uid, bulletin_lines, ['name', 'subtotal_employee'])
	list = {}
	for line in bulletin_lines:
		if line['name'][:4] == 'g320':
			line['name'] = 'g320'
		list[line['name']] = line['subtotal_employee']
        return list

    
    def get_journal(self, period_id, partner_id, department_id):
        employees = pooler.get_pool(self.cr.dbname).get('hr.employee')
	departments = employees.search(self.cr, self.uid, [('department_id', 'child_of', department_id)])
	departments = employees.read(self.cr, self.uid, departments, ['department_id'])
	depts = []
	for dept in departments:
		depts.append(dept['department_id'][0])
	depts.append(0)
	depts = tuple(depts)
        sql = '''
        SELECT r.name,e.matricule,r.cin,c.date_start,c.date_end,e.birthday,b.salaire_net_a_payer,b.salaire_base,b.salaire_brute,
        b.salaire_brute_imposable,b.salaire_net,b.salaire_net_imposable,b.cotisations_employee,b.cotisations_employer,
        b.igr,b.prime,b.indemnite,b.avantage,b.exoneration,b.deduction,b.normal_hours,b.prime_anciennete,b.working_days,
        b.frais_pro,b.personnes,b.absence,b.employee_contract_id as contract
        FROM hr_payroll_ma_bulletin b
        LEFT JOIN hr_contract c on (b.employee_contract_id=c.id)
        LEFT JOIN hr_employee e on (b.employee_id=e.id)
        LEFT JOIN resource_resource r on (r.id=e.resource_id)
	LEFT JOIN hr_department d on (d.id=e.department_id)
        WHERE b.period_id=%s and d.id in %s
        order by e.matricule
        ''' % (period_id, depts)
        self.cr.execute(sql)
        journal = self.cr.dictfetchall()

        return journal
    
    def get_total(self, period_id, department_id):
        employee_ids = pooler.get_pool(self.cr.dbname).get('hr.employee')
        employee_ids = employee_ids.search(self.cr, self.uid, [('department_id', 'child_of', department_id)])
        salaire_base = 0
        salaire_brute = 0
        salaire_brute_imposable = 0
        salaire_net_a_payer = 0
        salaire_net_imposable = 0
        cotisations_employee = 0
        cotisations_employer = 0
        igr = 0
        prime = 0
        indemnite = 0
        avantage = 0
        exoneration = 0
        deduction = 0
        normal_hours = 0
        prime_anciennete = 0
        working_days = 0
        frais_pro = 0
        personnes = 0
        absence = 0
	employees = 0
	comms = 0
	rappel = 0
	cnaps = 0
	medicale = 0
        tolal_line = {}
        bulletins = self.pool.get('hr.payroll_ma.bulletin')
        bulletins_ids = bulletins.search(self.cr, self.uid, [('employee_id', 'in', employee_ids), ('period_id', '=', int(period_id))])
        liste = bulletins.read(self.cr, self.uid, bulletins_ids, [])
        bulletin_line = pooler.get_pool(self.cr.dbname).get('hr.payroll_ma.bulletin.line')
        for b in liste:
	    bulletin_lines = bulletin_line.search(self.cr, self.uid, [('id_bulletin', '=', b['id'])])
            bulletin_lines = bulletin_line.read(self.cr, self.uid, bulletin_lines, ['name', 'subtotal_employee'])
            list = {}
            for line in bulletin_lines:
            	if line['name'][:4] == 'g320':
			prime_anciennete += line['subtotal_employee']
                if line['name'][:4] == 'g400':
			comms += line['subtotal_employee']                	
                if line['name'] in ['Prime divers', '3700 - Commissions sur Vente']:
                        comms += line['subtotal_employee']
                if line['name'][:4] == 'Rapp':
                	rappel += line['subtotal_employee']
                if line['name'][:4] == 'CNaP':
                        cnaps += line['subtotal_employee']
                if line['name'][:4] == 'SMIA':
                        medicale += line['subtotal_employee']
                if line['name'][:4] == 'FUNH':
                        medicale += line['subtotal_employee']
                if line['name'][:4] == 'OSTI':
                        medicale += line['subtotal_employee']
                if line['name'] == 'Salaire de base':
                        salaire_base += line['subtotal_employee']



#            salaire_base+=b['salaire_base']
            salaire_brute += b['salaire_brute']
            salaire_brute_imposable += b['salaire_brute_imposable']
            salaire_net_a_payer += b['salaire_net_a_payer']
            salaire_net_imposable += b['salaire_net_imposable']
            cotisations_employee += b['cotisations_employee']
            cotisations_employer += b['cotisations_employer']
            igr += b['igr']
            prime += b['prime']
            indemnite += b['indemnite']
            avantage += b['avantage']
            exoneration += b['exoneration']
            deduction += b['deduction']
            normal_hours += b['normal_hours']
            working_days += b['working_days']
            frais_pro += b['frais_pro']
            personnes += b['personnes']
            absence += b['absence']
            employees += 1
        liste = []
        print igr
        total_line = {
            'salaire_base':salaire_base,
            'salaire_brute':salaire_brute,
            'salaire_brute_imposable':salaire_brute_imposable,
            'salaire_net_a_payer':salaire_net_a_payer,
            'salaire_net_imposable':salaire_net_imposable,
            'cotisations_employee':cotisations_employee,
            'cotisations_employer':cotisations_employer,
            'igr':igr,
            'prime':prime,
            'indemnite':indemnite,
            'avantage':avantage,
            'exoneration':exoneration,
            'deduction':deduction,
            'normal_hours':normal_hours,
            'prime_anciennete':prime_anciennete,
            'working_days':working_days,
            'frais_pro':frais_pro,
            'personnes':personnes,
            'absence':absence,
            'employees':employees,
            'cnaps':cnaps,
            'medicale':medicale,
            'comms':comms,
            'rappel':rappel
            }
        liste.append(total_line)
        return liste

report_sxw.report_sxw('report.journal.paie', 'hr.payroll_ma.bulletin', 'syst_hr_payroll_ma/report/journal_paie_report.rml', journal_paie_report)
       
       
               
