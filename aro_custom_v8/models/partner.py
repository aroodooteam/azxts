#-*- coding:utf-8 -*-

"""A pypi demonstration vehicle.

.. moduleauthor:: Andrew Carter <andrew@invalid.com>

"""
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import pyodbc
import datetime
import decimal
from openerp import netsvc
import ast
import logging
_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
    """Description """
    _inherit = 'res.partner'

    _columns = {
        'v_neuf': fields.boolean('Client V9'),
        'stat': fields.char('Stat',size=32),
        'cif': fields.char('CIF',size=32),
        'agency_id': fields.many2one('base.agency', 'Agency', help='Agency assigned'),
    }

    def v9_fetch_invoice(self,cr,uid,ids,context=None):
        invoice_obj=self.pool.get('account.invoice')
        invoice_line_obj=self.pool.get('account.invoice.line')
        product_obj=self.pool.get('product.product')
        for partner in self.browse(cr,uid,ids,context):
            invoices=[]
            _logger.info(partner)
            v9_partner_id=partner.ref
            param_obj=self.pool.get('ir.config_parameter')
            connect_string=param_obj.get_param(cr,uid,'db.connect.param')
            con = pyodbc.connect(connect_string)
            cura = con.cursor()
            sql="""SELECT
                            PRM_IDENT,
                            PRM_DATE,
                            PRM_DATFINPER
                            from F_PRIME
                            where
                            PRM_PTRCLIIDENT = (
                               select
                                BPCL_IDENT from F_P_C_CLIENT
                                where
                            BPCL_PTRBPPIDENT=%s)"""%partner.ref
            cura.execute(sql)
            liste_facture=[]

            map={
                'PRM_IDENT':'internal_number',
                'PRM_DATE':'date_invoice',
                'PRM_DATFINPER':'comment'
            }

            columns = [column[0] for column in cura.description]

            for row in cura:
                compteur_line=0 #compteur de colonne de row
                data={}
                note='fin du contrat: '
                for col in columns:
                    if type(row[compteur_line])==datetime.datetime and map[col]=='comment':
                        note += row[compteur_line].strftime("%m-%d-%Y")
                        data[map[col]]=note
                    elif type(row[compteur_line])==datetime.datetime and map[col]!='comment':
                        data[map[col]] = row[compteur_line].strftime("%m-%d-%Y")
                    elif type(row[compteur_line])==decimal.Decimal:
                        data[map[col]] = int(row[compteur_line])
                    else:
                        data[map[col]] = row[compteur_line]
                    compteur_line += 1

                liste_facture.append(data)

            for elt in liste_facture:

                print "-------------------element de facture: ",elt,"--------------"
                condition = [('internal_number','=',elt['internal_number'])]
                res = invoice_obj.search(cr,uid,condition)
                if res != []:
                    invoice_id=res[0]

                else:#si la facture n'existe pas encore
                    elt['account_id']=partner.property_account_receivable.id
                    elt['partner_id']=partner.id
                    invoice_id=invoice_obj.create(cr,uid,elt)
                invoices.append(invoice_id)
                #Creation Lignes de facture
                #SQL requete recuperation lignes de facture
                id_facture = elt['internal_number']
                cura.execute("""
                        select
                              F_PRIME_LIGNE.LPR_IDENT Id_lpr
                             ,F_PRIME_LIGNE.LPR_PTRPRMIDENT num_prime
                             ,F_PRIME_LIGNE.LPR_ASSCODCPT description
                             ,('{ ''LPR_TAXASSMT'': '+cast(F_PRIME_LIGNE.LPR_TAXASSMT as varchar)
                              +', ''LPR_PRIMENETTE'': '+ cast(F_PRIME_LIGNE.LPR_PRIMENETTE as varchar)
                              +', ''LPR_FRACIE'': '+cast(F_PRIME_LIGNE.LPR_FRACIE as varchar)
                              +'}') PRIX
                        from F_PRIME_LIGNE where F_PRIME_LIGNE.LPR_PTRPRMIDENT = '%s'
                            and F_PRIME_LIGNE.LPR_ASSCODCPT is not null AND LPR_ASSCODCPT not like 'TVA'
                            AND LPR_ASSCODCPT not like 'TVA_AC'
                            """%(id_facture))

                liste_ligne_facture = []
                map={'Id_lpr':'origin',
                    'num_prime':'invoice_id',
                    'description':'name',
                    'PRIX':'price_unit'}

                titre_ligne_facture = [column[0] for column in cura.description]
                TE=0
                PN=0
                T=False
                nouvdict={}
                for row in cura:
                    count=0
                    invoice_line_data={}
                    for col in titre_ligne_facture:
                        if type(row[count])==decimal.Decimal:
                            invoice_line_data[map[col]]=int(row[count])
                        elif type(row[count])==str:
                            if row[count][0]=='{':
                                d = ast.literal_eval(row[count])
                                print(d)
                                TE+=d['LPR_TAXASSMT']
                                PN+=d['LPR_PRIMENETTE']
                                if row[count-1]=='FRAIS':
								    T=False
								    print(map[col])
								    invoice_line_data[map[col]]=d['LPR_FRACIE']
                                elif row[count-1]!='FRAIS':
                                    print(map[col])
                                    T=True
                                    invoice_line_data[map[col]]=PN
                                    nouvdict=invoice_line_data
                            else:
                                invoice_line_data[map[col]]=row[count]
						#invoice_line_data[map[col]]=row[count]
                        count+=1
                    if T!=True:
                        print('insertion de: ',invoice_line_data)
                        liste_ligne_facture.append(invoice_line_data)
                    else:
						#nouvdict=invoice_line_data
                        T=False
                nouvdict['name']='PRMNET'
                liste_ligne_facture.append(nouvdict)
                test = {'origin': 000000000, 'invoice_id': id_facture,'name': 'TE'}
                test['price_unit'] = TE
                liste_ligne_facture.append(test)
                print(liste_ligne_facture)
                for invoice_line in liste_ligne_facture:
                    invoice_line['quantity']=1
                    condition_ligne = [('origin','=',invoice_line['origin'])]
                    res_id_ligne = invoice_line_obj.search(cr,uid,condition_ligne)
                    if res_id_ligne == []:
                        print 'Insertion d\'une nouvelle ligne pour la facture: ',invoice_line['invoice_id']
                    #verification du produit dans la ligne
                        condition_produit=[('default_code','=',invoice_line['name'])]
                        res_liste_produit = product_obj.search(cr,uid, condition_produit)
                        if type(res_liste_produit)==list:
                            product_id=res_liste_produit[0]
                        else:
                            product_id=res_liste_produit

                        invoice_line['invoice_id'] = invoice_id
                        invoice_line['product_id'] = product_id
                        #creation de la ligne
                        id_ligne_facture = invoice_line_obj.create(cr,uid,invoice_line)
                        onchange_data=invoice_line_obj.product_id_change(cr,uid,
                                                    id_ligne_facture,
                                                    invoice_line['product_id'],1,
                                                    invoice_line['quantity'],
                                                    '',
                                                    'out_invoice',
                                                    elt['partner_id'])
                        onchange_data=onchange_data['value']
                        onchange_data['price_unit']=invoice_line['price_unit']
                        onchange_data['invoice_line_tax_id']=[(6,0,onchange_data['invoice_line_tax_id'])]
                        id_ligne_facture = invoice_line_obj.write(cr,uid,[id_ligne_facture],onchange_data)
        wf_service = netsvc.LocalService('workflow')
        for inv in invoices:
            validation=wf_service.trg_validate(uid, 'account.invoice', inv, 'invoice_open', cr)
            _logger.info(validation)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Factures',
            'view_type': 'form',
            'view_mode': 'tree,form',
            'context': context,
            'domain' : [('partner_id','=',partner.id),('state','=','open')],
            'res_model': 'account.invoice',
            'nodestroy': True,
        }


    def v9_create(self,cr,uid,ids,context=None):
        param_obj=self.pool.get('ir.config_parameter')
        connect_string=param_obj.get_param(cr,uid,'db.connect.param')
        con_sqlsrv = pyodbc.connect(connect_string)
        cur = con_sqlsrv.cursor()
        for partner in self.browse(cr,uid,ids):
            v9_partner_id=9900000000+partner.id
            result=cur.execute("""INSERT INTO F_P_PERSONNE (
            F_P_PERSONNE.BPP_SOCIETE,
            F_P_PERSONNE.BPP_IDENT,
            F_P_PERSONNE.BPP_TITRE,
            F_P_PERSONNE.BPP_NOM_1,
            F_P_PERSONNE.BPP_NOM_APPEL,
            F_P_PERSONNE.BPP_TEL_1,
            F_P_PERSONNE.BPP_EMAIL)
              VALUES  ('*****','%s','MR','%s','%s','%s','%s')"""%(v9_partner_id,partner.name,partner.name,partner.phone,partner.email))
            result=con_sqlsrv.commit()
            _logger.info(result)

            ads = partner.street
            ads1 = str(ads[0:59])

            v9_partner_adres = 999999000000+partner.id
            result=cur.execute("""insert into F_P_ADRESSE(
                BPA_IDENT,
                BPA_PTRBPPIDENT,
                BPA_ADR_NUM,
                BPA_ADR_TYPE,
                BPA_AD_LIG1,
                BPA_AD_LIG2,
                BPA_AD_PAYS_CODE,
                BPA_AD_PAYS_LIBEL,
                BPA_AD_CODPOST
            )values('%s','%s','1','%s','%s','%s','MG','Madagascar','%s')"""%(v9_partner_adres,v9_partner_id,ads1,ads1,partner.street2,partner.zip))

            result=con_sqlsrv.commit()
            _logger.info(result)


            v9_partner_bnq_id = 9999999900000+partner.id
            result=cur.execute("""insert into F_P_CORD_BNQ(
            F_P_CORD_BNQ.BPB_PTRBPPIDENT,
            F_P_CORD_BNQ.BPB_ISO_PAYS,
            F_P_CORD_BNQ.BPB_IDENT,
            BPB_CRD_NUM
            )values('%s','MG','%s','1') """%(v9_partner_id,v9_partner_bnq_id))
            result=con_sqlsrv.commit()


        con_sqlsrv.close()
        self.write(cr,uid,ids,{'ref':v9_partner_id,'v_neuf':True})
        return True

res_partner()

