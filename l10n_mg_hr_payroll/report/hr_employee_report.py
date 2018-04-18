import time 
from report import report_sxw 
class l10n_mg_hr_payroll(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(l10n_mg_hr_payroll, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 
        'time': time,
        }) 
report_sxw.report_sxw('report.hr.employee.attestation', 'hr.employee', 'addons/l10n_mg_hr_payroll/report/attestation.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.contract.avenant', 'hr.contract', 'addons/l10n_mg_hr_payroll/report/avenant.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.contract.certificate', 'hr.contract', 'addons/l10n_mg_hr_payroll/report/certificate.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.contract.ficheembauche', 'hr.contract', 'addons/l10n_mg_hr_payroll/report/ficheembauche.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.contract.frenchcontract', 'hr.contract', 'addons/l10n_mg_hr_payroll/report/frenchcontract.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.contract.malagasycontract', 'hr.contract', 'addons/l10n_mg_hr_payroll/report/malagasycontract.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.employee.sanction', 'hr.employee.sanction', 'addons/l10n_mg_hr_payroll/report/sanction.rml', parser=l10n_mg_hr_payroll, header=False) 
report_sxw.report_sxw('report.hr.employee.medical.ticket', 'hr.employee.medical.ticket', 'addons/l10n_mg_hr_payroll/report/medical.rml', parser=l10n_mg_hr_payroll, header=False)
report_sxw.report_sxw('report.hr.employee.departfunhece', 'hr.employee', 'addons/l10n_mg_hr_payroll/report/departfunhece.rml', parser=l10n_mg_hr_payroll, header=False)
report_sxw.report_sxw('report.hr.employee.cnapsrequest', 'hr.employee', 'addons/l10n_mg_hr_payroll/report/cnapsrequest.rml', parser=l10n_mg_hr_payroll, header=False)
report_sxw.report_sxw('report.hr.employee.groupedcnapsrequest', 'hr.employee', 'addons/l10n_mg_hr_payroll/report/groupedcnaps.rml', parser=l10n_mg_hr_payroll, header=False)
report_sxw.report_sxw('report.hr.employee.cancelbankletter', 'hr.employee', 'addons/l10n_mg_hr_payroll/report/cancelbankletter.rml', parser=l10n_mg_hr_payroll, header=False)


