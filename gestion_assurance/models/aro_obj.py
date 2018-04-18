# -*- coding: utf-8 -*-
###############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015-Today NextHope Business Solutions <contact@nexthope.net>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###########################################################################
from openerp import fields, models, api
from openerp.exceptions import Warning, ValidationError, except_orm
import openerp.addons.decimal_precision as dp
from datetime import datetime

class f_polices(models.Model):
    _name = 'f.polices'    
    
    
    name = fields.Char(string='Nom',) 
    POL_ASSURE = fields.Char(string="Souscripteur", )
    POL_NUMPOL = fields.Char(string="N° police", )
    POL_NUM_DOSSIER = fields.Char(string="N° de dossier")   
    POL_DATE_HEURE_EFFET = fields.Datetime(string="Date effet", )    
    POL_FRACTION =  fields.Char(string="Fractionnement")
    POL_CODECHPRIN = fields.Char(string="Ech.principale")
    POL_DUREE = fields.Char(string="Duree de contrat")
    POL_DATFIN = fields.Date(string="Date de fin")
    POL_COEF_COMM = fields.Float(string="Coef.commercial")
    POL_TAUX_APPEL = fields.Float(string="Taux d'appel")
    POL_DATEFIN_GRATUIT = fields.Datetime(string="Fin de periode de gratuit au")
    POL_CARENCE = fields.Float(string="Delai de carence")
    POL_UNITE_CARENCE = fields.Char(string="Unite de carence")
    POL_SANTE_NONRESP = fields.Boolean(string="Contrat non responsable")
    POL_OPTION = fields.Char(string="Option")
    POL_PTRCONVID_IJ = fields.Float(string="Convention IJ")
    POL_COAREP_PRM = fields.Char(string="Repartition des primes")
    POL_COMAPETX = fields.Float(string="Commission Aperiteur")
    POL_COAREP_SIN = fields.Char(string="Repartition des sinistres")
    
    
    POL_TERFISC = fields.Char(string="Territoire fiscal")
    POL_CODINDICE = fields.Char(string="Indice principal")
    POL_INDICEACTU = fields.Float(string="Valeur")
    
    POL_JOUR_PRELEVEMENT = fields.Float(string="Nb de prelevements")
    POL_CHARGECLIENT = fields.Char(string="Charge Clientelle")
    
    POL_CODE_SOCIETE = fields.Char(string="Societe")
    POL_CODE_ETABL = fields.Char(string="Etablissement")
    POL_COMMENTAIRES = fields.Text(string="Commentaires")
    
    ajout_risque = fields.Boolean(string="Ajout Risque")
    
    
    
    state = fields.Selection([
                 ('brouillon', "Devis"),
                 ('encours', "Contrat"),
                 ('suspension', "Suspension"), 
                 ('termine', "Termine"),   
                  ('annule', "Sans effet"),              
            ], default='brouillon',)
    
    POL_CODETAT = fields.Char(string="Code etat")
    
    ######## SOUSCRIPTEUR ###################################
    
    #########################################################
    
    ##### Liaison f_sit_objet_risque one2many ##########################################
    #POL_SOR_IDENT = fields.One2many('f.sit.objet.risque', 'SOR_PTRPOLID','Objet Risque')    
    ##### Liaison f_mouvement one2many ##########################################
    ################ Liaison f_version_police #########################################
    POL_VER_IDENT = fields.One2many('f.version.police','VER_PTRPOLID','Version Police')
    ###################################################################################
    #POL_MVT_IDENT = fields.One2many('f.mouvement', 'MVT_PTRPOLID','Mouvement')
    ################ Liaison produit assurance ##############################
    POL_PTRPASID = fields.Many2one('f.produitass','Produit assurance')
    ################## Liaison Polices apporteur ###########################
    POL_PTRAPID = fields.Many2one('f.apporteur','Apporteur')
    ################# Liaison Police et f_intermediaire #################
    POL_PTRINID = fields.Many2one('f.intermediaire','Intermediaire')
    
    ################# Liaison police client ############################
    POL_PTRCLID = fields.Many2one('f.p.c.client','Client')
    POL_BPCL_BPP_NAME = fields.Char(related='POL_PTRCLID.BPCL_BPP_NAME')
    POL_BPCL_CODE_AUXIL = fields.Char(related='POL_PTRCLID.BPCL_CODE_AUXIL')
    POL_BPCL_COTE = fields.Char(related='POL_PTRCLID.BPCL_COTE')
    ####################################################################
    
    ################### Liaison compagnies #################
    POL_PTRCOID = fields.Many2one('f.compagnies','Compagnie')
    ################# Liaison societe ######################
    
    
    def police_confirmed(self, cr, uid, ids, context=None):        
        self.write(cr,uid,ids,({'POL_CODETAT':'1','state':'encours'}),context)
        
    def police_ensuspension(self, cr, uid, ids, context=None):        
        self.write(cr,uid,ids,({'POL_CODETAT':'3','state':'suspension'}),context) 
        
    
    def police_cancel(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,({'POL_CODETAT':'96','state':'annule'}),context)
    
    #POL_PRODUCT = fields.Many2one('product.product', string="Produit")
    
class f_sit_objet_risque(models.Model):
    _name = 'f.sit.objet.risque'    
    
    name = fields.Char(string="Nom")
    SOR_CODE_PRODUCT = fields.Char(string="Code", )
    SOR_SERVICES = fields.Char(string="Service", )
    SOR_TABLE = fields.Char(string="Table")
    SOR_FORMULE = fields.Char(string="Formule")
    SOR_VA_FORCEE = fields.Char(string="SOR_VA_FORCEE",)
    ##### Liaison f_polices many2one ################################################
    SOR_PTRPOLID = fields.Many2one('f.polices','POLICE')
    ##### Liaison garantie (product.template) one2many  #############################
    SOR_GAD_IDENT = fields.One2many('f.garantie.dyn', 'GAD_PTRSORID','Garantie',domain=[('GAD_PRIME_NETTE', '!=', 0)])
    SOR_GAD_SOUSCRIPTION = fields.Char(related='SOR_GAD_IDENT.GAD_SOUSCRIPTION')
    ############## Liaison f_desc_stat_25 #####################
    ################ Liaison f_desc_stat_100 ##################
    SOR_D100_IDENT =  fields.One2many('f.desc.stat.100','D100_PTRSORID','Desc stat 100')
    ###########################################################
    ############## Liaison f_mouvement ########################    
    SOR_PTRSOROBJETID = fields.One2many('f.mouvement','MVT_PTRSOR_OBJET','Mouvement')
    SOR_DATEFIN = fields.Datetime(string="Date Fin")
    SOR_DATEFIN_FACT = fields.Datetime(string="Date Fin Fait")
    SOR_DATEDEBUT = fields.Datetime(string="Date de debut")
    ###########################################################
    #SOR_DST_IDENT = fields.One2many('f.desc.stat.25','DST_PTRSORIDENT','Desc Stat')
    
class f_mouvement(models.Model):
    _name = 'f.mouvement'
    
    MVT_CODETYPE = fields.Char(string="Type de mouvement",)    
    MVT_ZONEMODIFIEE = fields.Char(string="Zone modifiee",)
    MVT_DATEDEFFET = fields.Date(string="Date effet",)
    MVT_AVTSOR =  fields.Char(string="avt sor")
    ########### Liaison mouvement version police ###############
    MVT_PTRVERID =  fields.Many2one('f.version.police','Version Police')
    ########################### Liaison polices f_mouvement  #################
    MVT_PTRPOLID = fields.Many2one('f.polices','Police')
    ################ Mouvement et F_sit_objet_risque ####################
    MVT_PTRSOR_OBJET = fields.Many2one('f.sit.objet.risque','Risque')
    ####################################################################    
    

    
class f_garantie_dyn(models.Model):
    _name = 'f.garantie.dyn'
    
    name = fields.Char(string="Nom")
    GAD_CODE = fields.Char(string="Code") 
    GAD_SOUSCRIPTION = fields.Char(string="Souscription")   
    GAD_TAXES = fields.Float(string="Taxe")
    GAD_PRIME_NETTE = fields.Float(string="Prime nette")
    GAD_CODE_FISCAL  = fields.Char(string="Code fiscal")
    GAD_PTRSORID = fields.Many2one('f.sit.objet.risque','Objet Risque')
    
    
    
    
class f_produitass(models.Model):
    _name = 'f.produitass'
     
    name = fields.Char(string = "Nom")
    PAS_CODE_PRODUIT = fields.Char(string = "Code produit assurance")
    PAS_FRACT_POSSIBLE = fields.Char(string = "Fract possible")
    PAS_ITN01 = fields.Char(string ="Itn01")
    ########## Liaison f_polices ######################################
    PAS_POL_IDENT = fields.One2many('f.polices','POL_PTRPASID','Police')
    ######### Liaison produit assurance et branche many to one ###########
    PAS_PTRBASID = fields.Many2one('f.brancheass','Branche')
    PAS_NB_PROD_UTILI = fields.Integer(string="Numero produit assurance")
    
    
    
class f_brancheass(models.Model):
    _name = 'f.brancheass'
 
    name =  fields.Char(string="Nom de la branche")
    BAS_LIBELLE_BRANCHE = fields.Char(string="Nom branche")
    BAS_REF_EXTERNE = fields.Char(string="Reference externe")
    BAS_CODE_BRANCHE = fields.Char(string="Code branche", )
    #############  Liaison branche et produit assurance one to many ###################
    BAS_PAS_IDENT = fields.One2many('f.produitass', 'PAS_PTRBASID','Produit assurance')
    
    
class f_apporteur(models.Model):
    _name = 'f.apporteur'
    
    name = fields.Char(string="Nom apporteur")
    AP_CODE = fields.Char(string="Code apporteur")
    AP_VILLE = fields.Char(string="Ville")
    AP_PAYS = fields.Char(string="Pays")
    partner_id = fields.Many2one('res.partner', 'Partner', ondelete="cascade", select=True, auto_join=True)
    
    ################### Liaison f_apporteur police  ###################
    AP_POLIDENT = fields.One2many('f.polices','POL_PTRAPID','Police')
    
class f_intermediaire(models.Model):
    _name = 'f.intermediaire'
    
    name = fields.Char(string="Nom")
    IN_SL_CODE = fields.Char(string="Code")
    IN_TYPE = fields.Char(string="Type")
    TYPE = fields.Char(string="Type")
    IN_VILLE =  fields.Char(string="Ville")
    #################### Liaison Intermediaire Police #####################
    IN_POLIDENT = fields.One2many('f.polices','POL_PTRINID','Police')
    
class f_personne(models.Model):
    _name = 'f.p.personne'    
    
    
    name = fields.Char(string="Nom")
    PHYSIQUE = fields.Boolean(string="Personne physique")
    MORALE = fields.Boolean(string="Personne morale")
    BPP_TITRE = fields.Char(string="Civilite/forme")
    BPP_NOM_2 = fields.Char(string="Prenom/suite du nom")
    BPP_NOM_3 = fields.Char(string="Suite du nom")
    BPP_NOM_APPEL = fields.Char(string="Nom d'appel")
    BPP_NOM_ALIAS = fields.Char(string="Alias")
    EST_CLIENT = fields.Boolean(string="Prospect / Client")
    ############# Information generale ###################
    BPP_PP_SEXE = fields.Char(string="Sexe")
    BPP_PP_SITMATR = fields.Char(string="Situation familiale")
    BPP_PP_NO_SOCIAL = fields.Char(string="Numero social")
    BPP_PP_NAIS_DATE = fields.Date(string="Date de naissance")
    BPP_PP_RANG_NAISS = fields.Char(string="Rang de naissance")
    BPP_PP_NAIS_VIL_INSEE = fields.Char(string="Code INSEE de la ville de naissance")
    BPP_PP_NAIS_VILLE = fields.Char(string="Ville de naissance")
    BPP_PP_NAIS_DPT = fields.Char(string="Departement de naissance")
    BPP_PP_R_CATPROF = fields.Char(string="Categorie professionnelle")
    BPP_PP_R_PROF_CODE = fields.Char(string="Profession")
    BPP_PP_SIGNALEMENT = fields.Text(string="Signalement")
    BPP_PP_REV_TRANCHE = fields.Char(string="Tranche de revenu")
    BPP_PP_REV_VALEUR = fields.Float(string="Montant de revenu")
    BPP_PP_DECES_DATE = fields.Date(string="Date de deces")
    #####################################################
    
    ############## Autres informations si societe ##########
    BPP_PM_CA_VALEUR = fields.Float(string="Chiffe d'affaires")
    BPP_PM_EFF_NOMBRE = fields.Float(string="Effectifs en unites")
    BPP_PM_NOTATION = fields.Char(string="Notation financiere")
    BPP_PM_CODE_NAF = fields.Char(string="Code NAF")
    BPP_PM_NO_SIREN = fields.Char(string="Numero SIREN")
    BPP_PM_NO_SIRET = fields.Char(string="Numero SIRET")
    
    BPP_PM_NO_NACE = fields.Char(string="Code NACE")
    BPP_MAJ_INFO = fields.Date(string="Date de mise a jour des informations")
    
    BPP_PM_FORMJUR = fields.Char(string="Forme juridique")
    BPP_PM_CAPITAL = fields.Float(string="Capital source")
    BPP_PM_CA_TRANCHE = fields.Char(string="Tranche de CA")
    BPP_PM_EFF_TRANCHE = fields.Char(string="Tranche d'effectifs")
    
    BPP_PM_NO_APE = fields.Char(string="Nom d'appel")
    BPP_PM_DEST1_FONCT = fields.Char(string="Fonction")
    BPP_PM_DEST1_TEL = fields.Char(string="Tel")
    BPP_PM_DEST1_EMAIL = fields.Char(string="E-mail")
    BPP_PM_DEST2 = fields.Char(string="2nd contact")
    BPP_PM_DEST3 = fields.Char(string="3eme contact")
    
    
    ########################################################
    
    #### Liaison Adresse #################################    
    BPP_PP_NAIS_PAY_CODE = fields.Char(string="Pays")    
    BPP_BPA_IDENT = fields.One2many('f.p.adresse','BPA_PTRBPPIDENT','Adresse')
    BPA_BPP_PAYS_CODE = fields.Char(related='BPP_BPA_IDENT.BPA_AD_PAYS_CODE')
    BPA_BPP_PAYS_LIBEL = fields.Char(related="BPP_BPA_IDENT.BPA_AD_PAYS_LIBEL")
    BPA_PP_LIG1 = fields.Char(related="BPP_BPA_IDENT.BPA_AD_LIG1")
    BPA_PP_LOCALITE = fields.Char(related="BPP_BPA_IDENT.BPA_AD_LOCALITE")
    BPA_PP_CODPOST = fields.Char(related="BPP_BPA_IDENT.BPA_AD_CODPOST")
    BPA_PP_CEDEX = fields.Char(related="BPP_BPA_IDENT.BPA_AD_CEDEX")
    BPA_PP_VILLE = fields.Char(related="BPP_BPA_IDENT.BPA_AD_VILLE")
    BPA_PP_TYPE =  fields.Char(related="BPP_BPA_IDENT.BPA_ADR_TYPE")    
    ####### Adresse ################################
    
    ########### Poin de contact ####################
    BPP_TEL_1 = fields.Char(string="Tel. 1")
    BPP_TEL_2 = fields.Char(string="Tel. 2")
    BPP_TEL_3 = fields.Char(string="Tel. 3")
    BPP_TEL_3_POSTE = fields.Char(string="Poste")    
    BPP_TEL_FAX = fields.Char(string="Fax")
    BPP_TEL_TELEX = fields.Char(string="Telex")
    BPP_EMAIL = fields.Char(string="Email 1")
    BPP_EMAIL_2 = fields.Char(string="Email 2")
    BPP_SITE_WEB = fields.Char(string="Site web")
    ################################################
    
    ########### Cordonnes Bancaire ################
    BPB_BPP_PTRBPPIDENT = fields.One2many('f.p.cord.bnq','BPB_PTRBPPIDENT','Cordonnes bancaires')
    BPB_BPP_ISO_PAYS = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_ISO_PAYS')
    BPB_BPP_IBAN = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_IBAN')
    BPB_BPP_RIBF_COMPTE = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_RIBF_COMPTE')
    BPB_BPP_SWIFT = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_SWIFT')
    BPB_BPP_RIBF_BANQUE = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_RIBF_BANQUE')
    BPB_BPP_RIBF_GUICHET = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_RIBF_GUICHET')   
    BPB_BPP_RIBF_TITULAIRE = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_RIBF_TITULAIRE')
    BPB_BPP_RIBF_LIBELLE = fields.Char(related='BPB_BPP_PTRBPPIDENT.BPB_RIBF_LIBELLE')
    ###############################################
    
    
    ########## Personne est Client ##############################################################
    BPB_BPCL_PTRBPPIDENT = fields.One2many('f.p.c.client','BPCL_PTRBPPIDENT','Prospect / Client')
    BPCL_BPP_CODE_AUXIL = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_CODE_AUXIL')
    BPCL_BPP_COTE = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_COTE')
    BPCL_BPP_R_FAMILLE = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_FAMILLE')
    BPCL_BPP_R_SS_FAM = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_SS_FAM')
    BPCL_BPP_R_REGROUP1 = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_REGROUP1')
    BPCL_BPP_R_REGROUP2 = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_REGROUP2')
    BPCL_BPP_R_REGROUP3 = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_REGROUP3')
    BPCL_BPP_R_SECTEUR = fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_R_SECTEUR')
    BPCL_BPP_DATE_OUV_CPT = fields.Date(related='BPB_BPCL_PTRBPPIDENT.BPCL_DATE_OUV_CPT')
    BPCL_BPP_DATE_CLO_CPT = fields.Date(related='BPB_BPCL_PTRBPPIDENT.BPCL_DATE_CLO_CPT')
    BPCL_BPP_G_MODEREGL= fields.Char(related='BPB_BPCL_PTRBPPIDENT.BPCL_G_MODEREGL')
    BPCL_BPP_G_TYPE_PREL = fields.Selection(related='BPB_BPCL_PTRBPPIDENT.BPCL_G_TYPE_PREL')
    BPCL_BPP_CODE_PERSONNEL = fields.Boolean(related='BPB_BPCL_PTRBPPIDENT.BPCL_CODE_PERSONNEL')   
    ############################################################################################
    
    ######## Intervenant sur Objet de Risque #####################################
    #BPP_BPASS_PTRBPPIDENT = fields.One2many('f.p.c.assure','BPASS_PTRBPPIDENT','Intervenant sur objet de risque')
    ##############################################################################
    
    BPP_FISC_TERR = fields.Char(string="Territoire fiscal")
    BPP_LANGUE_CODE = fields.Char(string="Code langue")
    BPP_LANGUE_LIBEL = fields.Char(string="Langue")
    BPP_COMMENTAIRE = fields.Text(string="Commentaire")
    BPP_REF_EXTERNE = fields.Char(string="Ref. externe / Cote")
    BPP_PP_NB_ENFANTS = fields.Float(string="Nombre d'enfant")    
    BPP_PP_NAIS_DATE = fields.Date(string="Date de naissance")
    BPP_CRT_DATE = fields.Date(string="Date de creation")
    partner_id = fields.Many2one('res.partner',ondelete='cascade')
    
    
    
    def create(self, cr, uid, vals, context=None):         
        vals_res_partner = {'name':vals['name'],'street':vals['BPA_PP_LIG1'],'street2':vals['BPA_PP_LOCALITE'],
                            'city':vals['BPA_PP_VILLE'],'zip':vals['BPA_PP_CODPOST'],'partner_type':'personne'}         
         
        id_partner = self.pool.get('res.partner').create(cr,uid,vals_res_partner,context)        
        vals['partner_id'] = id_partner        
        id_personne = super(f_personne,self).create(cr,uid,vals,context=None)
        
        #adresse
        vals_f_p_adresse = {'BPA_PTRBPPIDENT':id_personne,'BPA_AD_PAYS_CODE':vals['BPA_BPP_PAYS_CODE'],'BPA_AD_PAYS_LIBEL':vals['BPA_BPP_PAYS_LIBEL'],
                            'BPA_AD_LIG1':vals['BPA_PP_LIG1'],'BPA_AD_LOCALITE':vals['BPA_PP_LOCALITE'],
                            'BPA_AD_CODPOST':vals['BPA_PP_CODPOST'],'BPA_AD_VILLE':vals['BPA_PP_VILLE'],'BPA_AD_CEDEX':vals['BPA_PP_CEDEX'],
                            'BPA_ADR_TYPE':vals['BPA_PP_TYPE']} 
        
        #cord banque
        vals_f_p_cord_bnq = {'BPB_PTRBPPIDENT':id_personne,'BPB_ISO_PAYS':vals['BPB_BPP_ISO_PAYS'],'BPB_IBAN':vals['BPB_BPP_IBAN'],
                             'BPB_RIBF_COMPTE':vals['BPB_BPP_RIBF_COMPTE'],'BPB_SWIFT':vals['BPB_BPP_SWIFT'],'BPB_RIBF_BANQUE':vals['BPB_BPP_RIBF_BANQUE'],
                             'BPB_RIBF_GUICHET':vals['BPB_BPP_RIBF_GUICHET'],'BPB_RIBF_TITULAIRE':vals['BPB_BPP_RIBF_TITULAIRE'],
                             'BPB_RIBF_LIBELLE':vals['BPB_BPP_RIBF_LIBELLE']}  
        id_adresse = self.pool.get('f.p.adresse').create(cr,uid,vals_f_p_adresse,context)        
        
        id_cord_banque = self.pool.get('f.p.cord.bnq').create(cr,uid,vals_f_p_cord_bnq,context)
        
        #create client
        vals_client = {'BPCL_CODE_AUXIL':vals['BPCL_BPP_CODE_AUXIL'],'BPCL_COTE':vals['BPCL_BPP_COTE'],'BPCL_R_FAMILLE':vals['BPCL_BPP_R_FAMILLE'],'BPCL_R_SS_FAM':vals['BPCL_BPP_R_SS_FAM'],'BPCL_R_REGROUP1':vals['BPCL_BPP_R_REGROUP1'],
                       'BPCL_R_REGROUP2':vals['BPCL_BPP_R_REGROUP2'],'BPCL_R_REGROUP3':vals['BPCL_BPP_R_REGROUP3'],'BPCL_R_SECTEUR':vals['BPCL_BPP_R_SECTEUR'],'BPCL_DATE_OUV_CPT':vals['BPCL_BPP_DATE_OUV_CPT'],'BPCL_DATE_CLO_CPT':vals['BPCL_BPP_DATE_CLO_CPT'],
                       'BPCL_G_MODEREGL':vals['BPCL_BPP_G_MODEREGL'],'BPCL_G_TYPE_PREL':vals['BPCL_BPP_G_TYPE_PREL'],'BPCL_CODE_PERSONNEL':vals['BPCL_BPP_CODE_PERSONNEL'],'name':vals['name'],'BPCL_PTRBPPIDENT':id_personne}       
        
        id_client = self.pool.get('f.p.c.client').create(cr,uid,vals_client,context)           
        return id_personne
    
    
    
    
    
class t_etabliss(models.Model):
    _name = 't.etabliss'
    
    name = fields.Char(string="Nom etablissement")
    TA_CLE = fields.Char(string="Cle etablissement")
    TA_CODESOCIETE = fields.Char(string="Code societe")
    TA_SOCIE_VILLE = fields.Char(string="Ville")
    
class t_societe(models.Model):
    _name = 't.societe'
    
    name = fields.Char(string="Nom de la societe")
    TA_CODE = fields.Char(string="Code")
    TA_SOCIE_ADRES1 = fields.Char(string="Boite postale")
    TA_SOCIE_TELECO = fields.Char(string="Telephone")
    TA_SOCIE_VILLE = fields.Char(string="Ville")
    ####### LIAISON POLICE #######################
    
    
class f_compagnies(models.Model):
    _name = 'f.compagnies'
    
    name = fields.Char(string="Nom")
    CO_CODEAUXIL = fields.Char(string="Code")
    ########## liaison f_compagnies police ############
    CO_POL_IDENT =  fields.One2many('f.polices','POL_PTRCOID','Police')
    
#Reprise de la table res_partner
class res_partner(models.Model):    
    _inherit = 'res.partner'
    
    partner_type = fields.Char(string="Type")
    id_f_p_c_client = fields.Float(string="Id Client v9")
    
    
class f_p_c_client(models.Model):
    _name = 'f.p.c.client'
    
    name = fields.Char(string="Nom du client")
    BPCL_CODE_AUXIL = fields.Char(string="Numero Compte")
    BPCL_COTE = fields.Char(string="Numero Cote")
    BPCL_R_FAMILLE = fields.Char(string="Famille")
    BPCL_R_SS_FAM = fields.Char(string="Sous-famille")
    BPCL_R_REGROUP1 = fields.Char(string="Code regroupement1")
    BPCL_R_REGROUP2 = fields.Char(string="Code regroupement2")
    BPCL_R_REGROUP3 = fields.Char(string="Code regroupement3")
    BPCL_R_SECTEUR = fields.Char(string="Secteur commercial")
    BPCL_DATE_OUV_CPT = fields.Date(string="Date ouverture compte")
    BPCL_DATE_CLO_CPT = fields.Date(string="Date cloture compte")
    BPCL_G_MODEREGL= fields.Char(string="Mode de reglement")
    BPCL_G_TYPE_PREL = fields.Selection([
                                         ("par_prime", "Par prime"),
                                         ("par_police", "Par police"), 
                                         ("par_echeance", "Par echeance"),                                                       
                                    ],string='Type de prelevement',)
    BPCL_CODE_PERSONNEL = fields.Boolean(string="Code Personnel(OUI/NON)")
    
    ########## Liaison f_p_c_client vers police #############    
    BPCL_POL_IDENT = fields.One2many('f.polices','POL_PTRCLID','Police')
    ########## Liaison personne => donc personne devient client ##########
    BPCL_PTRBPPIDENT = fields.Many2one('f.p.personne','Personne',ondelete='set null')
    BPCL_BPP_NOM_APPEL = fields.Char(related='BPCL_PTRBPPIDENT.BPP_NOM_APPEL')
    BPCL_BPP_NAME = fields.Char(related='BPCL_PTRBPPIDENT.name')
    #####################################################################
    
    ############ Liaison client adresse ##################
    ###################################################
    
    
class f_desc_stat_25(models.Model):
    _name = 'f.desc.stat.25'
    
    name = fields.Char(string="Nom")
    ############ Liaison Objet risque ####################
    #DST_PTRSORIDENT = fields.Many2one('f.sit.objet.risque','Objet risque')
    
    
class f_p_adresse(models.Model):
    _name = 'f.p.adresse'
    
    name = fields.Char(string="Nom")
    BPA_PTRBPPIDENT = fields.Many2one('f.p.personne','Personne')
    BPA_AD_PAYS_CODE = fields.Char(string="Code Pays")
    BPA_AD_PAYS_LIBEL = fields.Char(string="Pays")
    BPA_AD_LIG1 = fields.Char(string="Adresse")
    BPA_AD_LOCALITE = fields.Char(string="Localite")
    BPA_AD_CODPOST = fields.Char(string="Code postal - ville")
    BPA_AD_CEDEX = fields.Char(string="Cedex")
    BPA_AD_VILLE = fields.Char(string="Ville")
    BPA_ADR_TYPE = fields.Char(string="Type d'adresse")
    

class f_p_cord_bnq(models.Model):
    _name = 'f.p.cord.bnq'
    
    name = fields.Char(string="Libelle")
    BPB_PTRBPPIDENT = fields.Many2one('f.p.personne','Personne')
    BPB_ISO_PAYS = fields.Char(string="Pays")
    BPB_IBAN = fields.Char(string="Code IBAN")
    BPB_RIBF_COMPTE = fields.Char(string="Compte BBAN")
    BPB_SWIFT = fields.Char(string="Swift / BIC")
    BPB_RIBF_BANQUE = fields.Char(string="Banque")
    BPB_RIBF_GUICHET = fields.Char(string="Guichet")
    BPB_RIBF_COMPTE = fields.Char(string="Compte")
    BPB_RIBF_TITULAIRE = fields.Char(string="Titulaire")
    BPB_RIBF_LIBELLE = fields.Char(string="Libelle")
    
class f_p_c_assure(models.Model):
    _name = 'f.p.c.assure'    
    
    name = fields.Char(string="libelle")
    #BPASS_PTRBPPIDENT = fields.Many2one('f.p.personne','Personne')
    
    

# class f_brancheass(models.Model):
#     _name = 'f.brancheass'
# 
#     BAS_LIBELLE_BRANCHE = fields.Char(string="Nom branche")
#     BAS_CODE_BRANCHE = fields.Char(string="Code branche", )
# 

# #
# #
# #
# class product_template(models.Model):
#     _inherit = 'product.template'
# 
#     PAS_LIBELLE_PRODUIT = fields.Char("Nom de l'article")
# 
# class f_sit_objet_risque(models.Model):
#     _name = 'f.sit.objet.risque'
# 
#     SOR_CODE_PRODUCT = fields.Char(string="SOR_CODE_PRODUCT", )
#     SOR_SERVICES = fields.Char(string="SOR_SERVICES", )
#
# class f_intermediaire(models.Model):
#     _name = 'f.intermediaire'
#
# class f_prime(models.Model):
#     _name = 'f.prime'
#
class f_version_police(models.Model):
    _name = 'f.version.police'
    
    VER_TYPEMISSION = fields.Char(string="Type de mission")
    VER_DATEDEB = fields.Date(string="Date de debut")
    VER_DATEFIN = fields.Date(string="Date fin")
    VER_PTRPOLID = fields.Many2one('f.polices','Police')
    ###### Liaison F Mouvement ########################
    VER_MVT_IDENT =  fields.One2many('f.mouvement','MVT_PTRVERID','Mouvement')    
    ####################################################
    VER_PTRPRMID = fields.Many2one('f.prime','Prime')
    
    
class f_prime(models.Model):
    _name = 'f.prime'
       
    name = fields.Char(string="Nom")
    PRM_TEXTE = fields.Char(string="Texte")
    PRM_NATURE = fields.Char(string="Nature")
    PRM_POLNUMERO = fields.Char(string="Numero")
    PRM_ENCSOLDE = fields.Float(string="Solde")
    PRM_DATE = fields.Date(string="Date")  
    PRM_DATDEBPER = fields.Date(string="Date de debut")  
    PRM_DATFINPER = fields.Date(string="Date fin")
    PRM_TTCCLIENT = fields.Float(string="Montant TTC Client")
    PRM_PRNTOTMT = fields.Float(string="Montant Total")
    PRM_TAXTOTMT = fields.Float(string="Taxe")
    ########## Prime ligne ##################
    PRM_LPRIDENT = fields.One2many('f.prime.ligne','LPR_PTRPRMIDENT','Ligne de prime',domain=[('LPR_ASSCODCPT', '!=', False)])
    PRM_LPR_ASSCODCPT = fields.Char(related="PRM_LPRIDENT.LPR_ASSCODCPT")
    ############ Liaison f.prime et version police #################
    PRM_VER_IDENT =  fields.One2many('f.version.police','VER_PTRPRMID','version police')
    POL_SOUSCRIPTEUR = fields.Char(related="PRM_VER_IDENT.VER_PTRPOLID.POL_ASSURE",string="Souscripteur")
    POL_CLIENT = fields.Char(related="PRM_VER_IDENT.VER_PTRPOLID.POL_PTRCLID.name",string="Client")
    
    
    
    
     ############# Code ###############
    @api.multi
    def generate_invoice(self):        
        print "passed here when generate invoice"        
        ####### all instance ####################
        objPartner = self.env['res.partner']
        objProduct = self.env['product.template']
        objAccountInvoice = self.env['account.invoice']
        objProductCategory = self.env['product.category']        
        #### Recuperation du client #############       
        id_f_p_c_client =  self.PRM_VER_IDENT.VER_PTRPOLID.POL_PTRCLID
        res_partner = objPartner.search([('id_f_p_c_client','=',id_f_p_c_client.id)])               
        partner_id = res_partner.id
        ########## On indique qu'il faut que la facture possède un client ##################        
        if not partner_id:
            raise ValidationError("Veuillez reseinger le client correspondant")
            return False
        ######### Recuperation de la catégorie d'article ###################################
        categ_id = self.PRM_VER_IDENT.VER_PTRPOLID.POL_PTRPASID.id
                
        #### Recuperation de l'artcile (product) et creationde l'invoice line ###########
        inv_line_values = []        
        if  self.PRM_LPRIDENT: 
            for prime_line in self.PRM_LPRIDENT:            
                if prime_line.LPR_ASSCODCPT  not in [False,"FRAIS", "TVA","TVAAC","FRIMP","FRTER"]:
                    product_search = objProduct.search([('name','=',prime_line.LPR_ASSCODCPT),('categ_id','=',categ_id)])                    
                    product =  product_search                                            
                    ##### determiner la taxe te ####################                    
                    te = 'Te-'+ str(prime_line.LPR_TAXASSTX)                                                          
                    id_taxe = self.env['account.tax'].search([('description','=', te)])                                      
                    id_line_tax = False                    
                    ################ New added ###################                                    
                    if prime_line.LPR_TAXASSTF == 'Z':
                        if id_taxe: 
                            tva = 35                          
                            if te == 'Te-3':
                                tva = 45
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4':
                                tva = 46
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4.5':                                
                                tva = 42
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                                print id_line_tax
                            if te == 'Te-7':
                                tva = 37
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-20':
                                tva = 36
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            
                    if prime_line.LPR_TAXASSTF == 'E':
                        if id_taxe: 
                            tva = 35                        
                            if te == 'Te-0':
                                tva = 50
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTX == 'B':
                        if id_taxe:
                            tva = 35                        
                            if te == 'Te-0':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTF == 'U':                        
                        if id_taxe:
                            tva = 35                           
                            if te == 'Te-3':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4.5':
                                tva == 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-7':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-20':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTF == 'T':
                        if id_taxe:
                            tva = 35
                            if te == 'Te-14.5':
                                tva = 48
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                                
                                    
#                   #############################################
                    product_account_id = objProduct.browse([product.id])
                    product_account_account_id = product_account_id.property_account_income
                    inv_line_values.append([0, False, {
                                                       'uos_id': 5, 
                                                       'product_id':product.id,
                                                       'account_id':product_account_account_id.id,
                                                       'name':product.description_sale,
                                                       'price_unit':prime_line.LPR_PRIMENETTE,
                                                       'discount': 0, 
                                                       'invoice_line_tax_id': id_line_tax,                                                       
                                                       'account_analytic_id': False,                                                    
                                                       'quantity': 1,                                                   
                                                       }
                                            ])     
                ########## Recuperation de l accessoire #######################
                if prime_line.LPR_ASSCODCPT in [True,"FRAIS","FRIMP","FRTER"]:
                    te = 'Te-'+ str(prime_line.LPR_TAXASSTX)                                          
                    id_taxe = self.env['account.tax'].search([('description','=', te)])                                        
                    id_line_tax = False                                       
                    ################ New added ###################                                    
                    if prime_line.LPR_TAXASSTF == 'Z':
                        if id_taxe: 
                            tva = 35                          
                            if te == 'Te-3':
                                tva = 45
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4':
                                tva = 46
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4.5':                                
                                tva = 42
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                                print id_line_tax
                            if te == 'Te-7':
                                tva = 37
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-20':
                                tva = 36
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            
                    if prime_line.LPR_TAXASSTF == 'E':
                        if id_taxe: 
                            tva = 35                        
                            if te == 'Te-0':
                                tva = 50
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTX == 'B':
                        if id_taxe:
                            tva = 35                        
                            if te == 'Te-0':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTF == 'U':                        
                        if id_taxe:
                            tva = 35                           
                            if te == 'Te-3':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-4.5':
                                tva == 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-7':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                            if te == 'Te-20':
                                tva = 35
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]
                    if prime_line.LPR_TAXASSTF == 'T':
                        if id_taxe:
                            tva = 35
                            if te == 'Te-14.5':
                                tva = 48
                                id_line_tax =   [[6, False, [id_taxe.id,tva]]]                                
                                           
                    ##############################################                                                               
                    
                    ##### recuperation accessoire ###################  
                    ########## Append accesoire on invoice line like a product#################
                    self.env.cr.execute('SELECT SUM("LPR_FRACIE") FROM f_prime_ligne WHERE "LPR_PTRPRMIDENT" = %s AND "LPR_ASSCODCPT" LIKE %s',(self.id,'FR',))
                    dataAcc = self.env.cr.fetchall()
                   
                    accessoire = 0.0
                    if dataAcc:            
                        dataAccessoire = dataAcc[0][0]            
                        if dataAccessoire is not None:
                            accessoire = float(dataAccessoire)                     
                        
                    #### append on invoice line ###############   10711 : accessoire     
                    product_accessoire = objProduct.browse([10711])               
                    inv_line_values.append([0, False, {
                                                       'uos_id': 5, 
                                                       'product_id':product_accessoire.id,
                                                       'name':product_accessoire.name,
                                                       'account_id':9814,
                                                       'price_unit':accessoire,
                                                       'discount': 0,                                            
                                                       'invoice_line_tax_id': id_line_tax,
                                                       'account_analytic_id': False,                                                    
                                                       'quantity': 1,                                                                                              
                                                       }
                                          ]) 
                           
        else:
            raise ValidationError("Ligne de prime inexistant")
            return False
		
		######## GET currency of company ################
        currency = self.env.ref('base.main_company').currency_id
		####### GET partner account id #####################
        #res_account_id = objPartner.browse([partner_id])
        #res_account_account_id = res_account_id.property_account_receivable
		#################################################
              
        ###### Creation de la facture ####################
        inv_values = {  'comment': False, 
                        'currency_id': currency.id, 
                        'fiscal_position': False, 
                        'user_id': 1, 
                        'account_id': 8529, 
                        'partner_bank_id': False,
                        'payment_term': False, 
                        'tax_line': [], 
                        'section_id': False, 
                        'journal_id': 1, 
                        'company_id': 1, 
                        'date_invoice': False,
                        'origin': False, 
                        'date_invoice':datetime.now(),
                        'date_due':datetime.now(), 
                        'period_id': False, 
                        'message_follower_ids': False, 
                        'partner_id': partner_id, 
                        'message_ids': False, 
                        'invoice_line':inv_line_values,
                        'name': False,                      
                        'amount_total':self.PRM_TTCCLIENT,
                        }
        
        invoice_ids = objAccountInvoice.sudo().create(inv_values) 
        ####################### Reset button taxes ###################################"
        self.pool.get('account.invoice').button_reset_taxes(self.env.cr, self.env.uid, [invoice_ids.id], context=None)    
        #########################Set is_invoiced 1#######################################   
        self.write({'is_invoiced':True,'invoice_id':invoice_ids.id})        
        invoice_form = self.env.ref('account.invoice_form', False) 
        
                     
        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'views': [(invoice_form.id, 'form')],
            'view_id': invoice_form.id,
            'res_id':invoice_ids.id,
            'context': "{'type': 'out_invoice'}",   
            'target': 'current',           
             
        }
        
    @api.multi
    def open_invoice_prime(self):        
        invoice_form = self.env.ref('account.invoice_form', False)
          
        return {
            'name': 'Customer Invoices',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'account.invoice',
            'views': [(invoice_form.id, 'form')],
            'view_id': invoice_form.id,
            'res_id':self.invoice_id,
            'context': "{'type': 'out_invoice'}",   
            'target': 'current',           
            
        }       

        
        
    
    
    
class f_desc_stat_100(models.Model):
    _name = 'f.desc.stat.100'
    
    name = fields.Char(string="Nom")
    D100_DESC_00 = fields.Char(string="Tarif")
    D100_DESC_01 = fields.Char(string="N° Immatriculation")
    D100_DESC_02 = fields.Char(string="Marque et Type")
    D100_DESC_03 = fields.Char(string="Carrosserie")
    D100_DESC_04 = fields.Char(string="Usage")
    D100_DESC_05 = fields.Char(string="N° de Serie")
    D100_DESC_06 = fields.Char(string="Date de premiere mise en circulation")
    D100_DESC_07 = fields.Char(string="Puissance fiscale(Exprimee en CV)")
    D100_DESC_08 = fields.Char(string="Source d'energie")
    D100_DESC_09 = fields.Char(string="Poids a vide")
    D100_DESC_10 = fields.Char(string="Poids Total en Charge (kg)")
    D100_DESC_11 = fields.Char(string="Nombre de Places")
    D100_DESC_12 = fields.Char(string="Remorque ou Semi-remorque")
    D100_DESC_13 = fields.Char(string="Periode de validite de la visite technique - Du")
    D100_DESC_14 = fields.Char(string="- Au")
    D100_DESC_15 = fields.Char(string="N° de la vignette")
    D100_DESC_16 = fields.Char(string="N° de la vignette patente")
    D100_DESC_17 = fields.Char(string="N° de l'attestation d'assurance")
    D100_DESC_18 = fields.Char(string="Reduction pour expertise prealable")
    D100_DESC_19 = fields.Char(string="Avis expertise prealable pour garantie B")
    D100_DESC_20 = fields.Char(string="Transport de matieres inflammables")
    D100_DESC_21 = fields.Char(string="Reduction-Majoration (%)")
    D100_DESC_22 = fields.Char(string="Vehicule Assure Hors taxe")
    
    ########## Liaison avec objet risque ############################
    D100_PTRSORID = fields.Many2one('f.sit.objet.risque','Risque')    
    #################################################################
    
    
#     
class f_prime_ligne(models.Model):
    _name = 'f.prime.ligne'
       
    LPR_PRIMENETTE = fields.Float(string="Prime nette")
    LPR_REVTIETYP = fields.Char(string="Type")
    LPR_COMAPPCR = fields.Char(string="Come ppcr")
    LPR_REGREVCR = fields.Char(string="Reg rev cr")
    LPR_TAXASSMT  = fields.Float(string="Taxe SSMT")
    LPR_REVTYP = fields.Char(string="Type")
    LPR_REVTOTAL = fields.Float(string="Total")
    LPR_REVRESTE = fields.Float(string="Reste")
    LPR_ASSCODCPT = fields.Char(string="Code")
    LPR_FRACIE = fields.Float(string="Fracie")
    LPR_TAXASSMT = fields.Float(string="Taxe")
    LPR_TAXASSTX = fields.Float(string="Taux taxe")
    
    ####### Liasion PRIME#############################
    LPR_PTRPRMIDENT = fields.Many2one('f.prime','Prime')
#     
    
    
       
    
    
