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

class f_prime(models.Model):
    _inherit = 'f.prime'
    
    is_invoiced = fields.Boolean(string="Possede une facture",default=False)
    invoice_id = fields.Integer(string="Facture")
    PRM_CAPITAL = fields.Char()
    PRM_SMP = fields.Char()
    PRM_TAUX_FAC = fields.Char()
    PRM_NUMERO=fields.Char()
    PRM_PTRCLIIDENT = fields.Float()
    PRM_PTRINTID = fields.Float()
    PRM_PTRAPID = fields.Float()
    PRM_ETABLISSEMENT = fields.Char()
    PRM_PTRPRAIDENT = fields.Float()
    
    
    
class f_prime_ligne(models.Model):
    _inherit = 'f.prime.ligne'
    LPR_TAXASSTF = fields.Char()
    
class f_mouvement(models.Model):
    _inherit = 'f.mouvement'
    state = fields.Char(string="Etat")
    
class f_desc_stat_100(models.Model):
    _inherit = 'f.desc.stat.100'
    D100_DESC_23 = fields.Char()
    D100_DESC_24 = fields.Char()
    D100_DESC_25 = fields.Char()
    D100_DESC_26 = fields.Char()
    D100_DESC_27 = fields.Char()
    D100_DESC_28 = fields.Char()
    D100_DESC_29 = fields.Char()
    D100_DESC_30 = fields.Char()
    D100_DESC_31 = fields.Char()
    D100_DESC_32 = fields.Char()
    D100_DESC_33 = fields.Char()
    D100_DESC_34 = fields.Char()
    D100_DESC_35 = fields.Char()
    D100_DESC_36 = fields.Char()
    D100_DESC_37 = fields.Char()
    D100_DESC_38 = fields.Char()
    D100_DESC_39 = fields.Char()
    D100_DESC_40 = fields.Char()
    D100_DESC_41 = fields.Char()
    D100_DESC_42 = fields.Char()
    D100_DESC_43 = fields.Char()
    D100_DESC_44 = fields.Char()
    D100_DESC_45 = fields.Char()
    D100_DESC_46 = fields.Char()
    D100_DESC_47 = fields.Char()
    D100_DESC_48 = fields.Char()
    D100_DESC_49 = fields.Char()
    D100_DESC_50 = fields.Char()
    D100_DESC_51 = fields.Char()
    D100_DESC_52 = fields.Char()
    D100_DESC_53 = fields.Char()
    D100_DESC_54 = fields.Char()
    D100_DESC_55 = fields.Char()
    D100_DESC_56 = fields.Char()
    D100_DESC_57 = fields.Char()
    D100_DESC_58 = fields.Char()
    D100_DESC_59 = fields.Char()
    D100_DESC_60 = fields.Char()
    D100_DESC_61 = fields.Char()
    D100_DESC_62 = fields.Char()
    D100_DESC_63 = fields.Char()
    D100_DESC_64 = fields.Char()
    D100_DESC_65 = fields.Char()
    D100_DESC_66 = fields.Char()
    D100_DESC_67 = fields.Char()
    D100_DESC_68 = fields.Char()
    D100_DESC_69 = fields.Char()
    D100_DESC_70 = fields.Char()
    D100_DESC_71 = fields.Char()
    D100_DESC_72 = fields.Char()
    
    D100_DESC_73 = fields.Char()
    D100_DESC_74 = fields.Char()
    D100_DESC_75 = fields.Char()
    D100_DESC_76 = fields.Char()
    D100_DESC_77 = fields.Char()
    D100_DESC_78 = fields.Char()
    D100_DESC_79 = fields.Char()
    D100_DESC_80 = fields.Char()
    D100_DESC_81 = fields.Char()
    D100_DESC_82 = fields.Char()
    D100_DESC_83 = fields.Char()
    D100_DESC_84 = fields.Char()
    D100_DESC_85 = fields.Char()
    D100_DESC_86 = fields.Char()
    D100_DESC_87 = fields.Char()
    D100_DESC_88 = fields.Char()
    D100_DESC_89 = fields.Char()
    D100_DESC_90 = fields.Char()
    D100_DESC_91 = fields.Char()
    D100_DESC_92 = fields.Char()
    D100_DESC_93 = fields.Char()
    D100_DESC_94 = fields.Char()
    D100_DESC_95 = fields.Char()
    D100_DESC_96 = fields.Char()
    D100_DESC_97 = fields.Char()
    D100_DESC_98 = fields.Char()
    D100_DESC_99 = fields.Char()
    D100_DESC_100 = fields.Char()
    
    
    
    
    
class f_clause_dyn(models.Model):    
    _name = 'f.clause.dyn'
        
    CLD_TABLE = fields.Char()
    CLD_INT_LOT_EXP = fields.Char()
    CLD_IDENT = fields.Float()
    CLD_REFECHO = fields.Char()
    CLD_PTRSSRID = fields.Float()
    CLD_SEQUENTIEL = fields.Float()
    CLD_CHAPITRE = fields.Char()
    CLD_S_CHAPITRE = fields.Char()
    CLD_TYPE = fields.Float()
    CLD_INT_LOT_IMP = fields.Char()
    CLD_CODE = fields.Char()
    CLD_SERVICES = fields.Char()
    CLD_SS_CHAPITRE = fields.Char()
    CLD_LIBRE = fields.Float()
    CLD_ORDRE = fields.Float()
    CLD_TEXTE = fields.Char()
    CLD_PTRSORID = fields.Many2one('f.sit.objet.risque','Risque')
    
    
class f_sit_objet_risque(models.Model):
    _inherit = 'f.sit.objet.risque'
    
    SOR_CLD_IDENT =  fields.One2many('f.clause.dyn','CLD_PTRSORID','Clause')   
    SOR_AD_IDENT = fields.One2many('f.maladie.adher','AD_PTRSORID','Maladie adher')
    GAD_PTRAYID = fields.Many2one('f.maladie.ay.dr','Maladie ayant droit')
    
class f_maladie_adher(models.Model):
    _name = 'f.maladie.adher'
    
    AD_NOMAPPEL = fields.Char(string="Nom d'appel")
    AD_TITRE = fields.Char(string="Titre")
    AD_NOMDE1 = fields.Char()
    AD_NOMDE2 = fields.Char()
    AD_DATNAISS = fields.Date(string="Date de naissance")
    AD_SEXE = fields.Char(string="Sexe")
    AD_COMMENT = fields.Char(string="Commentaire")
    AD_TELEPHONE = fields.Char(string="Telephone")
    AD_PTRBPPIDENT = fields.Float()
    AD_PTRBPAIDENT = fields.Float()
    AD_PTRSORID = fields.Many2one('f.sit.objet.risque','Risque') 
    AD_PTRBPASSIDENT = fields.Float()
    AD_PTRRIBIDENT = fields.Float()
    AD_IDENT = fields.Float()
    AY_AD_IDENT = fields.One2many('f.maladie.ay.dr','AY_PTRADID','Maladie ayant droit')
    
    
class  f_maladie_ay_dr(models.Model):
    _name = 'f.maladie.ay.dr'
    
    AY_IDENT = fields.Float()
    AY_PTRADID = fields.Many2one('f.maladie.adher','Maladie adher')
    AY_ORIGPTR = fields.Float()
    AY_PTRSORIDENT = fields.Float()
    AY_PTRBPPIDENT = fields.Float()
    AY_NOMAPPEL = fields.Char(string="Nom d'appel")
    AY_NOM = fields.Char(string="Nom")
    AY_PRENOM = fields.Char(string="prenom")
    AY_NUM_SS = fields.Char()
    AY_CLE_NUM_SS = fields.Char()
    AY_DATE_NAISS = fields.Date()
    AY_SEXE = fields.Char(string="Sexe")
    AY_COMMENTAIRE = fields.Char(string="Commentaire")
    AY_NOM2 = fields.Char()
    AY_INT_LOT_EXP = fields.Char()
    AY_INT_LOT_IMP = fields.Char()
    AY_DTCRE = fields.Date(string="Date creation")
    AY_LASER = fields.Char()
    AY_DTMAJ = fields.Date()
    AY_REFECHO = fields.Char()
    AY_REGIME_SALARIE = fields.Char(string="Regime salarial")
    AY_PTRBPASSIDENT = fields.Float()
    AY_NOEMIE = fields.Float()
    AY_TP_PHARMA = fields.Float()
    AY_REMB_SS = fields.Float()
    AY_TYPE_TAUX_SS = fields.Char()
    AY_DATEDEBUT = fields.Date(string="Date de debut")
    AY_DATEFIN = fields.Date(string="Date fin")
    AY_SS = fields.Char()
    AY_PTRCONVID = fields.Float()
    AY_PTRCONVID_IJ = fields.Float()
    AY_GADIDENT = fields.One2many('f.garantie.dyn','GAD_PTRAYID','Garantie')
   
    
class f_garantie_dyn(models.Model):
    _inherit = 'f.garantie.dyn'
    
    GAD_PTRAYID = fields.Many2one('f.maladie.ay.dr','Maladie ayant droit')
    GAD_LIBELLE = fields.Char()
    
    
    
    
        
    
    
    
    
    
      