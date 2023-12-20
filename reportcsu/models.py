from tokenize import String
from django.db import models
from django.db.models import Q
from core import models as core_models
from medical.models import Item, Service
from report.services import run_stored_proc_report
from claim.models import Claim, ClaimService, ClaimItem, ClaimServiceService, ClaimServiceItem
from location.models import Location, HealthFacility
from policy.models import Policy
from insuree.models import Insuree
from collections import defaultdict
from django.db.models import Count
from django.db.models import F
from insuree.models import Insuree
from insuree.models import InsureePolicy
import json
import datetime
from program import models as program_models
import time


val_de_zero = [
    'million', 'milliard', 'billion',
    'quadrillion', 'quintillion', 'sextillion',
    'septillion', 'octillion', 'nonillion',
    'décillion', 'undecillion', 'duodecillion',
    'tredecillion', 'quattuordecillion', 'sexdecillion',
    'septendecillion', 'octodecillion', 'icosillion', 'vigintillion'
]

to_19_fr = (
    'zéro', 'un', 'deux', 'trois', 'quatre', 'cinq', 'six',
    'sept', 'huit', 'neuf', 'dix', 'onze', 'douze', 'treize',
    'quatorze', 'quinze', 'seize', 'dix-sept', 'dix-huit', 'dix-neuf'
)

tens_fr  = (
    'vingt', 'trente', 'quarante', 'cinquante', 'soixante', 'soixante',
    'quatre-vingts', 'quatre-vingt'
)

denom_fr = (
    '', 'mille', 'million', 'milliard', 'billion', 'quadrillion',
    'quintillion', 'sextillion', 'septillion', 'octillion', 'nonillion',
    'décillion', 'undecillion', 'duodecillion', 'tredecillion',
    'quattuordecillion', 'sexdecillion', 'septendecillion',
    'octodecillion', 'icosillion', 'vigintillion'
)

denoms_fr = (
    '', 'mille', 'millions', 'milliards', 'billions', 'quadrillions',
    'quintillions', 'sextillions', 'septillions', 'octillions', 'nonillions',
    'décillions', 'undecillions', 'duodecillions', 'tredecillions',
    'quattuordecillions', 'sexdecillions', 'septendecillions',
    'octodecillions', 'icosillions', 'vigintillions'
)

def invoice_csu_query(user, **kwargs):
    print("AAAAAA")
    date_from = kwargs.get("date_from")
    date_to = kwargs.get("date_to")
    location0 = kwargs.get("location0")
    location1 = kwargs.get("location1")
    location2 = kwargs.get("location2")
    hflocation = kwargs.get("hflocation")
    
    format = "%Y-%m-%d"

    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")

    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")

    dictGeo = {}
    dictBase = {
        "dateFrom": date_from_str,
        "dateTo": date_to_str
    }
    # If there is HealthFacility defined in the form
    if hflocation and hflocation!="0" :
        hflocationObj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocationObj.name
        dictGeo['health_facility'] = hflocationObj.id
    
    # Get all 5 Programs
    today = datetime.datetime.now()
    programs = program_models.Program.objects.filter(
        validityDateFrom__lte=today).filter(
        Q(validityDateTo__isnull=True) | Q(validityDateTo__gte=today)
        ).exclude(code='DNB').order_by('-idProgram')[:5]
    
    program_ids = []
    for prg in programs:
        program_ids.append(prg)
    number = len(program_ids)
    # Complete to 5 elements if the result is less than 5
    while number < 5:
        program_ids.append(0)
        number += 1

    invoiceElemtTotal_MontantRecueTotal = 0
    invoiceElemtTotal_MtnValideTotal = 0
    i = 1
    for program in program_ids:
        if i == 1:
            dictBase.update({
                "prestationForfaitaire" : [],
                "prestationPlafonnees" : [],
                "prestationsNonMedicales" : [],
                "invoiceElemtTotal": [],
                "Program1": program.nameProgram if program != 0 else " "
            })
        else:
            dictBase.update({
                "prestationForfaitaireProgram"+str(i): [],
                "prestationPlafonneesProgram"+str(i): [],
                "prestationsNonMedicalesProgram"+str(i) : [],
                "invoiceElemtTotalProgram"+str(i): [],
                "Program"+str(i): program.nameProgram if program != 0 else " "
            })
        ## Get All claim corresponding to parameter sent
        statusExcluded = [1, 2]
        value = program.idProgram if program != 0 else 0
        claimList = Claim.objects.exclude(
            status__in=statusExcluded
        ).filter(
            date_to__gte=date_from,
            date_to__lte=date_to,
            validity_to__isnull=True,
            program=value,
            **dictGeo
        )

        invoiceElemtList = defaultdict(dict)
        invoiceElemtTotal = defaultdict(int)
        invoiceElemtListP = []
        invoiceElemtListF = []
        invoiceElemtListS = []


        for cclaim in claimList:
            #First we calculate on each Service inside a
            claimService = ClaimService.objects.filter(
                claim = cclaim,
                status=1
            ).filter(validity_to__is_null=True)
            for claimServiceElmt in claimService:
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] = 0
                if claimServiceElmt.service.id not in invoiceElemtList[claimServiceElmt.service.packagetype]:
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id] = defaultdict(dict)
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = defaultdict(int)
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] = 0

                ## Define global information of each Line
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["name"] = claimServiceElmt.service.name
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["code"] = claimServiceElmt.service.code
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"] = claimServiceElmt.service.price
                ## Status Valuated of Claim
                if cclaim.status==16:
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'] += int(claimServiceElmt.qty_provided)
                    if claimServiceElmt.price_valuated == None :
                        claimServiceElmt.price_valuated = 0
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'] += int(claimServiceElmt.qty_provided * claimServiceElmt.price_valuated)

                    invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'])
                    invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'])

                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] += claimServiceElmt.qty_provided
                ## Specific Rules for Montant Recue (for different type of package)
                if claimServiceElmt.service.packagetype == "S":
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += claimServiceElmt.qty_provided * invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"]
                else :
                    # Desactivation du controle sur ManualPrice
                    #if claimServiceElmt.service.manualPrice == True :
                    #    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += claimServiceElmt.qty_provided * claimServiceElmt.service.price
                    #else :
                    claimSs = ClaimServiceService.objects.filter(
                        claimlinkedService = claimServiceElmt
                    )
                    tarifLocal = 0
                    for claimSsElement in claimSs:
                        tarifLocal += claimSsElement.qty_displayed * claimSsElement.price_asked
                    #    print(tarifLocal)
                    claimSi = ClaimServiceItem.objects.filter(
                        claimlinkedItem = claimServiceElmt
                    )
                    for claimSiElement in claimSi:
                        tarifLocal += claimSiElement.qty_displayed * claimSiElement.price_asked
                        #print(tarifLocal)
                    #print(type(tarifLocal))
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += tarifLocal
            
                
                if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
                    invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(int)

                ### Sum of all line at footer of table
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyTotalV"] += int(claimServiceElmt.qty_provided)
                MtnNotValideV = 0
                if int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotalV"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"]) > 0:
                    MtnNotValideV = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotalV"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"])
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValideV"] = MtnNotValideV
                invoiceElemtTotal["QtyTotalV"] += int(claimServiceElmt.qty_provided)

            #Then we calculate on each Item inside a claim
            # claimItem = ClaimItem.objects.filter(
            #     claim = cclaim,
            #     status=1
            # )
            # for claimItemElmt in claimItem:
            #     if claimItemElmt.service.id not in invoiceElemtList[claimItemElmt.service.packagetype]:
            #         invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id] = defaultdict(int)

            #     if cclaim.status == "16":
            #         invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated'] += claimItemElmt.qty_provided

            #     invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["name"] = claimItemElmt.service.name
            #     invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["code"] = claimItemElmt.service.code
            #     invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"] = claimItemElmt.price_asked
            #     invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["all"] += claimItemElmt.qty_provided
            #     invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["MontantRecue"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['all'] * invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"]            
                
            #     if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
            #         invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(int)

            #     invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyTotalV"] += claimItemElmt.qty_provided
            #     invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyValuatedV"] += int(invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated'])
            #     invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValideV"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['sum']
            #     MtnNotValideV = 0
            #     if invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotal"] - invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValide"] > 0:
            #         MtnNotValideV = invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotal"] - invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValide"]
            #     invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnNotValideV"] = MtnNotValideV
            #     invoiceElemtTotal["QtyTotalV"] += claimItemElmt.qty_provided
        
        invoiceElemtTotal["PQtyValuatedV"]=0
        invoiceElemtTotal["PMontantRecueTotalV"] = 0
        invoiceElemtTotal["PMtnNotValideV"] = 0
        invoiceElemtTotal["PMtnValideV"] = 0
        invoiceElemtTotal["FMontantRecueTotalV"] = 0
        invoiceElemtTotal["FQtyValuatedV"] = 0
        invoiceElemtTotal["FMtnNotValideV"] = 0
        invoiceElemtTotal["FMtnValideV"] = 0 
        invoiceElemtTotal["SQtyValuatedV"] = 0
        invoiceElemtTotal["SMontantRecueTotalV"] = 0
        invoiceElemtTotal["SMtnNotValideV"] = 0
        invoiceElemtTotal["SMtnValideV"] = 0
        
        # print ("{:<5} {:<5} {:<40} {:<10} {:<10} {:<10} {:<10} {:<20}".format('type','id','name','Code','tarif','qty', 'Montant Recus','Qty Validated'))
        # print("invoiceElemtList ", invoiceElemtList)
        for typeList,v in invoiceElemtList.items():
            for id in v:
                montantNonValide = 0
                # Correction des chiffres negatif : -- Si un montant est negatif ca veut dire que le montant valuated est superieur a la somme des sous-services / services
                # if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0 :
                montantNonValide = v[id]['MontantRecue'] - v[id]['qty']['sum']
                if typeList=="P":
                    invoiceElemtListP.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(montantNonValide)),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))

                    invoiceElemtTotal["PMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["PQtyValuatedV"] += v[id]['qty']['valuated']
                    PMtnNotValideV = 0
                    if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0:
                        PMtnNotValideV = v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["PMtnNotValideV"] += PMtnNotValideV
                    invoiceElemtTotal["PMtnValideV"] += v[id]['qty']['sum']

                if typeList=="F":
                    invoiceElemtListF.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(montantNonValide)),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))
                    invoiceElemtTotal["FMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["FQtyValuatedV"] += v[id]['qty']['valuated']
                    FMtnNotValideV = 0
                    if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0:
                        FMtnNotValideV = v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["FMtnNotValideV"] += FMtnNotValideV
                    invoiceElemtTotal["FMtnValideV"] += v[id]['qty']['sum']

                
                if typeList=="S":
                    invoiceElemtListS.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(v[id]['MontantRecue'] - v[id]['qty']['sum'])),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))
                    invoiceElemtTotal["SMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["SQtyValuatedV"] += v[id]['qty']['valuated']
                    invoiceElemtTotal["SMtnNotValideV"] += v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["SMtnValideV"] += v[id]['qty']['sum']

                # print("{:<5} {:<5} {:<40} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    # typeList, id, v[id]['name'], v[id]['code'], v[id]['tarif'],v[id]['qty']['all'], v[id]['MontantRecue'],v[id]['qty']['valuated']
                    # ))

        ## Calcaulating of each invoiceElemtTotal
        invoiceElemtTotal["NbFactureValideTotal"] = invoiceElemtTotal["FQtyValuatedV"] + invoiceElemtTotal["SQtyValuatedV"] + invoiceElemtTotal["PQtyValuatedV"]
        invoiceElemtTotal["NbFactureValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["NbFactureValideTotal"])
        invoiceElemtTotal["FQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["FQtyValuatedV"])
        invoiceElemtTotal["SQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["SQtyValuatedV"])
        invoiceElemtTotal["PQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["PQtyValuatedV"])
        invoiceElemtTotal["FQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["FQtyTotalV"])
        invoiceElemtTotal["SQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["SQtyTotalV"])
        invoiceElemtTotal["PQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["PQtyTotalV"])

        invoiceElemtTotal["MtnValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"]+invoiceElemtTotal["SMtnValideV"]+invoiceElemtTotal["PMtnValideV"])
        invoiceElemtTotal_MtnValideTotal += invoiceElemtTotal["FMtnValideV"]+invoiceElemtTotal["SMtnValideV"]+invoiceElemtTotal["PMtnValideV"]
        invoiceElemtTotal["FMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"])
        invoiceElemtTotal["SMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnValideV"])
        invoiceElemtTotal["PMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnValideV"])
        invoiceElemtTotal["MtnNonValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"]+invoiceElemtTotal["SMtnNotValideV"]+invoiceElemtTotal["PMtnNotValideV"])
        invoiceElemtTotal["FMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"])
        invoiceElemtTotal["SMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnNotValideV"])
        invoiceElemtTotal["PMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnNotValideV"])

        invoiceElemtTotal["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"]+invoiceElemtTotal["FMontantRecueTotalV"]+invoiceElemtTotal["SMontantRecueTotalV"])
        invoiceElemtTotal_MontantRecueTotal += invoiceElemtTotal["PMontantRecueTotalV"]+invoiceElemtTotal["FMontantRecueTotalV"]+invoiceElemtTotal["SMontantRecueTotalV"]
        print("invoiceE_____RecueTotal ", invoiceElemtTotal_MontantRecueTotal)
        print("invoiceElemtTotal_MtnValideTotal ", invoiceElemtTotal_MtnValideTotal)
        invoiceElemtTotal["PMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"])
        invoiceElemtTotal["SMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["SMontantRecueTotalV"])
        invoiceElemtTotal["FMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMontantRecueTotalV"])

        invoiceElemtTotal["QtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["QtyTotalV"])

        if i == 1:
            dictBase["prestationForfaitaire"] = invoiceElemtListP
            dictBase["prestationPlafonnees"] = invoiceElemtListF
            dictBase["prestationsNonMedicales"] = invoiceElemtListS
            dictBase["invoiceElemtTotal"] = invoiceElemtTotal
            print("Premier dict base est")
            print(dictBase["invoiceElemtTotal"])
        else:
            dictBase["prestationForfaitaireProgram"+str(i)] = invoiceElemtListP
            dictBase["prestationPlafonneesProgram"+str(i)] = invoiceElemtListF
            dictBase["prestationsNonMedicalesProgram"+str(i)] = invoiceElemtListS
            dictBase["invoiceElemtTotalProgram"+str(i)] = invoiceElemtTotal
            print(dictBase["invoiceElemtTotalProgram"+str(i)])
        i += 1
    print("invoiceElemtTotal_MontantRecueTotal is ", invoiceElemtTotal_MontantRecueTotal)
    print("invoiceElemtTotal_MtnValideTotal is ", invoiceElemtTotal_MtnValideTotal)
    # dictBase["invoiceElemtTotal"]["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MontantRecueTotal)
    # dictBase["invoiceElemtTotal"]["MtnValideTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MtnValideTotal)
    dictBase["MontnRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MontantRecueTotal)
    dictBase["MtnValideTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MtnValideTotal)
    
    # print(dictBase)

    if location0:
        location0_str = Location.objects.filter(
            code=location0,
            validity_to__isnull=True
            ).first().name
        dictBase["region"] = location0_str

    if location1:
        location1_str = Location.objects.filter(
            code=location1,
            validity_to__isnull=True
            ).first().name
        dictBase["district"] =location1_str
    if location2:
        location2_str = Location.objects.filter(
            code=location2,
            validity_to__isnull=True
            ).first().name
        dictBase["area"] = location2_str
    return dictBase


def _convert_nnn_fr(val):
    """
    \detail         convert a value < 1000 to french
        special cased because it is the level that kicks 
        off the < 100 special case.  The rest are
        more general.  This also allows you to
        get strings in the form of 'forty-five hundred' if called directly.
    \param  val     value(int or float) to convert
    \return         a string value
    """
    word = ''
    (mod, rem) = (val % 100, val // 100)
    if rem > 0:
        if (rem>1 and rem <10 and mod <= 0): 
             word = to_19_fr[rem] + ' cents'
        else: 
             word = to_19_fr[rem] + ' cent'
             
        if mod > 0:
            word += ' '
    if mod > 0:
        word += _convert_nn_fr(mod)
    return word

def _convert_nn_fr(val):
    """
    \brief       convert a value < 100 to French
    \param  val  value to convert 
    """
    if val < 20:
        return to_19_fr[val]
    for (dcap, dval) in ((k, 20 + (10 * v)) for (v, k) in enumerate(tens_fr)):
        if dval + 10 > val:
            if dval in (70,90):
                return dcap + '-' + to_19_fr[val % 10 + 10]
            if val % 10:
                return dcap + '-' + to_19_fr[val % 10]
            return dcap

def french_number(val):
    
    """
    \brief       Convert a numeric value to a french string
        Dispatch diffent kinds of number depending
        on their value (<100 or < 1000)
        Then create a for loop to rewrite cutted number.
    \param  val  value(int or float) to convert
    \return      a string value
    """
    
    if val < 100:
        return _convert_nn_fr(val)
    if val < 1000:
         return _convert_nnn_fr(val)
    for (didx, dval) in ((v - 1, 1000 ** v) for v in range(len(denom_fr))):
        if dval > val:
            mod = 1000 ** didx
            l = val // mod
            r = val - (l * mod)
            
            pref_final = _convert_nnn_fr(l)
            pref = pref_final.split(' ')
            if(pref[len(pref)-1] == ' cent'):
                pref[len(pref)-1] = " cents"
                pref_final = " ".join(x for x in pref)
            if l>1:    
                ret = pref_final + ' ' + denoms_fr[didx]
            else:
                ret = pref_final + ' ' + denom_fr[didx]
            if r > 0:
                ret = ret + ' ' + french_number(r)
            return ret

def amount_to_text_fr(number, currency):
    """
    \brief              convert amount value to french string
        reuse the french_number function
        to write the correct number
        in french, then add the specific cents for number < 0
        and add the currency to the string
    \param  number      the number to convert
    \param  currency    string value of the currency
    \return             the string amount in french
    """
    try:
        number = int(number)
    except:
        return 'Traduction error'
    number = '%.2f' % number
    units_name = currency
    list = str(number).split('.')
    start_word = french_number(abs(int(list[0])))

    #On enleve le un au debut de la somme écrite en lettre.
    liste = str(start_word).split(' ')
    for i in range(len(liste)):
        item = liste[i]
        tab=liste
        if item =='un':
            if i==0 and len(liste) > 1:
                if liste[i+1] not in val_de_zero:
                    tab[i]=""
            elif i > 0 and len(liste) > 1:
                if i < len(liste)-1:
                    if liste[i+1] not in val_de_zero:
                        if not liste[i-1] in ["cent", "cents"] and not (liste[i+1] in val_de_zero or liste[i+1] in denom_fr or liste[i+1] in denoms_fr):
                            tab[i]=""
            start_word = " ".join(x for x in tab)
    french_number(int(list[1]))
    final_result = start_word +' '+units_name
    return final_result
    
def invoice_hiv_query(user, **kwargs):
    date_from = kwargs.get("date_from")
    date_to = kwargs.get("date_to")
    hflocation = kwargs.get("hflocation")
    
    format = "%Y-%m-%d"
    
    maintenant = time.strftime("%d/%m/%Y %H:%M:%S")
    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")

    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")

    dictGeo = {}
    dictBase = {}
    total = 0
    element_ids = []
    dictBase["periode"] = str(date_from_str) + " - " + date_to_str
    dictBase["dateFacturation"] = maintenant
    dictBase["texte1"] = "Rapporté à ___________ le ..../..../20__"
    dictBase["texte2"] = "Vérifié à ________ le ..../..../20__"
    dictBase["texte3"] = "Validé le ______________________"
    dictBase["valeur1"] = "Responsable de l'établissement de santé (HHF)\n\n\n\n\n\n\n\n\n\n\n\n"
    dictBase["valeur2"] = "Auditeur CVA Responsable HF"
    dictBase["valeur3"] = "Comité de Validation"
    # If there is HealthFacility defined in the form
    if hflocation and hflocation!="0" :
        hflocationObj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocationObj.name
        dictBase["Phone"] = hflocationObj.phone
        dictGeo['health_facility'] = hflocationObj.id
        level_village = False
        level_district = False
        level_ville = False
        municipality = " "
        district = " "
        village = " "
        if hflocationObj.location.parent:
            level_district = True
            if hflocationObj.location.parent.parent:
                level_ville = True
                if hflocationObj.location.parent.parent.parent:
                    level_village = True
        if level_village:
            village = hflocationObj.location.name
            municipality = hflocationObj.location.parent.name
            district = hflocationObj.location.parent.parent.name
            region = hflocationObj.location.parent.parent.parent.name
        elif level_ville:
            municipality = hflocationObj.location.name
            district = hflocationObj.location.parent.name
            region = hflocationObj.location.parent.parent.name
        elif level_district:
            district = hflocationObj.location.name
            region = hflocationObj.location.parent.name
        else:
            region = hflocationObj.location.name
        print("region ", region)
        print("district ", district)
        print("municipality ", municipality)
        print("village ", village)
    
        dictBase["region"] = region
        dictBase["district"] = district
        dictBase["area"] = municipality
        dictBase["village"] = village

    data = []
    today = datetime.datetime.now()
    hivprogram = program_models.Program.objects.filter(
        validityDateFrom__lte=today).filter(
        Q(validityDateTo__isnull=True) | Q(validityDateTo__gte=today)
        ).filter(nameProgram__in=['VIH', 'vih', 'HIV', 'hiv']).first()
    if hivprogram:
        print(hivprogram.idProgram)
        claimList = Claim.objects.exclude(
            status=1
        ).filter(
            date_from__gte=date_from,
            date_from__lte=date_to,
            validity_to__isnull=True,
            program=hivprogram.idProgram,
            **dictGeo
        )

        count = 1
        for cclaim in claimList:
            claimService = ClaimService.objects.filter(
                claim = cclaim,
                status=1
            ).filter(validity_to__is_null=True)
            for claimServiceElmt in claimService:
                if claimServiceElmt.service:
                    if claimServiceElmt.service.program:
                        if claimServiceElmt.service.program.idProgram == hivprogram.idProgram:
                            if claimServiceElmt.service.id not in element_ids:
                                element_ids.append(claimServiceElmt.service.id)
                                qty_approved = claimServiceElmt.qty_approved and claimServiceElmt.qty_approved or 0
                                qty_provided = 0
                                if cclaim.status==16:
                                    # Valuated
                                    qty_provided = claimServiceElmt.qty_provided and claimServiceElmt.qty_provided or 0
                                pu = claimServiceElmt.service.price and claimServiceElmt.service.price or 0
                                sous_total = pu * qty_provided
                                total += sous_total
                                val = {
                                    "Numero": str(count),
                                    "Nom": claimServiceElmt.service.name,
                                    "QteDeclaree": str("{:,.0f}".format(float(qty_approved))),
                                    "QteValidee": str("{:,.0f}".format(float(qty_provided))),
                                    "PrixUnit": str("{:,.0f}".format(float(pu))),      
                                    "Montant": str("{:,.0f}".format(float(int(sous_total))))
                                }
                                data.append(val)
                                count +=1


            # claimItem
            claimItems = ClaimItem.objects.filter(
                claim = cclaim,
                status=1
            )
            for claimItemElmt in claimItems:
                if claimItemElmt.item.id not in element_ids:
                    element_ids.append(claimItemElmt.item.id)
                    qty_approved = claimItemElmt.qty_approved and claimItemElmt.qty_approved or 0
                    qty_provided = 0
                    if cclaim.status==16:
                        # Valuated
                        qty_provided = claimItemElmt.qty_provided and claimItemElmt.qty_provided or 0
                    pu = claimItemElmt.item.price and claimItemElmt.item.price or 0
                    sous_total2 = pu * qty_provided
                    total += sous_total2
                    val = {
                        "Numero": str(count),
                        "Nom": claimItemElmt.item.name,
                        "QteDeclaree": str("{:,.0f}".format(float(qty_approved))),
                        "QteValidee": str("{:,.0f}".format(float(qty_provided))),
                        "PrixUnit": str("{:,.0f}".format(float(pu))),   
                        "Montant": str("{:,.0f}".format(float(int(sous_total2))))
                    }
                    data.append(val)
                    count +=1
    dictBase["datas"] = data
    dictBase["TOTAL"] = str("{:,.0f}".format(float(int(total)))) + " Francs CFA"
    dictBase["amountLetter"] = amount_to_text_fr(int(total), 'Francs CFA')
    print("dictBase ", dictBase)
    return dictBase


def invoice_declaration_naissance_query(user, **kwargs):
    print("BBBB")
    date_from = kwargs.get("date_from")
    date_to = kwargs.get("date_to")
    location0 = kwargs.get("location0")
    location1 = kwargs.get("location1")
    location2 = kwargs.get("location2")
    hflocation = kwargs.get("hflocation")
    
    format = "%Y-%m-%d"

    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")

    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")

    dictGeo = {}
    dictBase = {
        "dateFrom": date_from_str,
        "dateTo": date_to_str
    }
    # If there is HealthFacility defined in the form
    if hflocation and hflocation!="0" :
        hflocationObj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocationObj.name
        dictGeo['health_facility'] = hflocationObj.id
    
    # Get all 5 Programs
    today = datetime.datetime.now()
    programs = program_models.Program.objects.filter(
        validityDateFrom__lte=today).filter(
        Q(validityDateTo__isnull=True) | Q(validityDateTo__gte=today)
        ).filter(code='DNB').order_by('-idProgram')[:5]
    
    program_ids = []
    for prg in programs:
        program_ids.append(prg)
    number = len(program_ids)
    # Complete to 5 elements if the result is less than 5
    while number < 5:
        program_ids.append(0)
        number += 1

    invoiceElemtTotal_MontantRecueTotal = 0
    invoiceElemtTotal_MtnValideTotal = 0
    i = 1
    for program in program_ids:
        dictBase.update({
            "prestationForfaitaireProgram"+str(i): [],
            "prestationPlafonneesProgram"+str(i): [],
            "prestationsNonMedicalesProgram"+str(i) : [],
            "invoiceElemtTotalProgram"+str(i): [],
            "Program"+str(i): program.nameProgram if program != 0 else " "
        })
        ## Get All claim corresponding to parameter sent
        statusExcluded = [1, 2]
        value = program.idProgram if program != 0 else 0
        claimList = Claim.objects.exclude(
            status__in=statusExcluded
        ).filter(
            date_to__gte=date_from,
            date_to__lte=date_to,
            validity_to__isnull=True,
            program=value,
            **dictGeo
        )

        invoiceElemtList = defaultdict(dict)
        invoiceElemtTotal = defaultdict(int)
        invoiceElemtListP = []
        invoiceElemtListF = []
        invoiceElemtListS = []


        for cclaim in claimList:
            #First we calculate on each Service inside a
            claimService = ClaimService.objects.filter(
                claim = cclaim,
                status=1
            ).filter(validity_to__is_null=True)
            for claimServiceElmt in claimService:
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] = 0
                if claimServiceElmt.service.id not in invoiceElemtList[claimServiceElmt.service.packagetype]:
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id] = defaultdict(dict)
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = defaultdict(int)
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] = 0

                ## Define global information of each Line
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["name"] = claimServiceElmt.service.name
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["code"] = claimServiceElmt.service.code
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"] = claimServiceElmt.service.price
                ## Status Valuated of Claim
                if cclaim.status==16:
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'] += int(claimServiceElmt.qty_provided)
                    if claimServiceElmt.price_valuated == None :
                        claimServiceElmt.price_valuated = 0
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'] += int(claimServiceElmt.qty_provided * claimServiceElmt.price_valuated)

                    invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'])
                    invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'])

                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] += claimServiceElmt.qty_provided
                ## Specific Rules for Montant Recue (for different type of package)
                if claimServiceElmt.service.packagetype == "S":
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += claimServiceElmt.qty_provided * invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"]
                else :
                    # Desactivation du controle sur ManualPrice
                    #if claimServiceElmt.service.manualPrice == True :
                    #    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += claimServiceElmt.qty_provided * claimServiceElmt.service.price
                    #else :
                    claimSs = ClaimServiceService.objects.filter(
                        claimlinkedService = claimServiceElmt
                    )
                    tarifLocal = 0
                    for claimSsElement in claimSs:
                        tarifLocal += claimSsElement.qty_displayed * claimSsElement.price_asked
                    #    print(tarifLocal)
                    claimSi = ClaimServiceItem.objects.filter(
                        claimlinkedItem = claimServiceElmt
                    )
                    for claimSiElement in claimSi:
                        tarifLocal += claimSiElement.qty_displayed * claimSiElement.price_asked
                        #print(tarifLocal)
                    #print(type(tarifLocal))
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] += tarifLocal
            
                
                if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
                    invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(int)

                ### Sum of all line at footer of table
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyTotalV"] += int(claimServiceElmt.qty_provided)
                MtnNotValideV = 0
                if int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotalV"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"]) > 0:
                    MtnNotValideV = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotalV"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"])
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValideV"] = MtnNotValideV
                invoiceElemtTotal["QtyTotalV"] += int(claimServiceElmt.qty_provided)
    
        invoiceElemtTotal["PQtyValuatedV"]=0
        invoiceElemtTotal["PMontantRecueTotalV"] = 0
        invoiceElemtTotal["PMtnNotValideV"] = 0
        invoiceElemtTotal["PMtnValideV"] = 0
        invoiceElemtTotal["FMontantRecueTotalV"] = 0
        invoiceElemtTotal["FQtyValuatedV"] = 0
        invoiceElemtTotal["FMtnNotValideV"] = 0
        invoiceElemtTotal["FMtnValideV"] = 0 
        invoiceElemtTotal["SQtyValuatedV"] = 0
        invoiceElemtTotal["SMontantRecueTotalV"] = 0
        invoiceElemtTotal["SMtnNotValideV"] = 0
        invoiceElemtTotal["SMtnValideV"] = 0
        
        # print ("{:<5} {:<5} {:<40} {:<10} {:<10} {:<10} {:<10} {:<20}".format('type','id','name','Code','tarif','qty', 'Montant Recus','Qty Validated'))
        # print("invoiceElemtList ", invoiceElemtList)
        for typeList,v in invoiceElemtList.items():
            for id in v:
                montantNonValide = 0
                # Correction des chiffres negatif : -- Si un montant est negatif ca veut dire que le montant valuated est superieur a la somme des sous-services / services
                # if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0 :
                montantNonValide = v[id]['MontantRecue'] - v[id]['qty']['sum']
                if typeList=="P":
                    invoiceElemtListP.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(montantNonValide)),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))

                    invoiceElemtTotal["PMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["PQtyValuatedV"] += v[id]['qty']['valuated']
                    PMtnNotValideV = 0
                    if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0:
                        PMtnNotValideV = v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["PMtnNotValideV"] += PMtnNotValideV
                    invoiceElemtTotal["PMtnValideV"] += v[id]['qty']['sum']

                if typeList=="F":
                    invoiceElemtListF.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(montantNonValide)),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))
                    invoiceElemtTotal["FMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["FQtyValuatedV"] += v[id]['qty']['valuated']
                    FMtnNotValideV = 0
                    if v[id]['MontantRecue'] - v[id]['qty']['sum'] > 0:
                        FMtnNotValideV = v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["FMtnNotValideV"] += FMtnNotValideV
                    invoiceElemtTotal["FMtnValideV"] += v[id]['qty']['sum']

                
                if typeList=="S":
                    invoiceElemtListS.append(dict(
                        name=v[id]['name'],
                        code=v[id]['code'],
                        tarif=str("{:,.0f}".format(v[id]['tarif'])),
                        nbrFacture = str(int(v[id]['qty']['all'])),
                        mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                        nbFactureValides= str(v[id]['qty']['valuated']),
                        montantNonValide = str("{:,.0f}".format(v[id]['MontantRecue'] - v[id]['qty']['sum'])),
                        montantValide =  str("{:,.0f}".format(v[id]['qty']['sum']))
                        ))
                    invoiceElemtTotal["SMontantRecueTotalV"] += v[id]['MontantRecue']
                    invoiceElemtTotal["SQtyValuatedV"] += v[id]['qty']['valuated']
                    invoiceElemtTotal["SMtnNotValideV"] += v[id]['MontantRecue'] - v[id]['qty']['sum']
                    invoiceElemtTotal["SMtnValideV"] += v[id]['qty']['sum']

                # print("{:<5} {:<5} {:<40} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                    # typeList, id, v[id]['name'], v[id]['code'], v[id]['tarif'],v[id]['qty']['all'], v[id]['MontantRecue'],v[id]['qty']['valuated']
                    # ))

        ## Calcaulating of each invoiceElemtTotal
        invoiceElemtTotal["NbFactureValideTotal"] = invoiceElemtTotal["FQtyValuatedV"] + invoiceElemtTotal["SQtyValuatedV"] + invoiceElemtTotal["PQtyValuatedV"]
        invoiceElemtTotal["NbFactureValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["NbFactureValideTotal"])
        invoiceElemtTotal["FQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["FQtyValuatedV"])
        invoiceElemtTotal["SQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["SQtyValuatedV"])
        invoiceElemtTotal["PQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["PQtyValuatedV"])
        invoiceElemtTotal["FQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["FQtyTotalV"])
        invoiceElemtTotal["SQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["SQtyTotalV"])
        invoiceElemtTotal["PQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["PQtyTotalV"])

        invoiceElemtTotal["MtnValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"]+invoiceElemtTotal["SMtnValideV"]+invoiceElemtTotal["PMtnValideV"])
        invoiceElemtTotal_MtnValideTotal += invoiceElemtTotal["FMtnValideV"]+invoiceElemtTotal["SMtnValideV"]+invoiceElemtTotal["PMtnValideV"]
        invoiceElemtTotal["FMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"])
        invoiceElemtTotal["SMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnValideV"])
        invoiceElemtTotal["PMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnValideV"])
        invoiceElemtTotal["MtnNonValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"]+invoiceElemtTotal["SMtnNotValideV"]+invoiceElemtTotal["PMtnNotValideV"])
        invoiceElemtTotal["FMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"])
        invoiceElemtTotal["SMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnNotValideV"])
        invoiceElemtTotal["PMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnNotValideV"])

        invoiceElemtTotal["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"]+invoiceElemtTotal["FMontantRecueTotalV"]+invoiceElemtTotal["SMontantRecueTotalV"])
        invoiceElemtTotal_MontantRecueTotal += invoiceElemtTotal["PMontantRecueTotalV"]+invoiceElemtTotal["FMontantRecueTotalV"]+invoiceElemtTotal["SMontantRecueTotalV"]
        print("invoiceE_____RecueTotal ", invoiceElemtTotal_MontantRecueTotal)
        print("invoiceElemtTotal_MtnValideTotal ", invoiceElemtTotal_MtnValideTotal)
        invoiceElemtTotal["PMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"])
        invoiceElemtTotal["SMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["SMontantRecueTotalV"])
        invoiceElemtTotal["FMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMontantRecueTotalV"])

        invoiceElemtTotal["QtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["QtyTotalV"])

        if i == 1:
            dictBase["prestationForfaitaire"] = invoiceElemtListP
            dictBase["prestationPlafonnees"] = invoiceElemtListF
            dictBase["prestationsNonMedicales"] = invoiceElemtListS
            dictBase["invoiceElemtTotal"] = invoiceElemtTotal
            print("Premier dict base est")
            print(dictBase["invoiceElemtTotal"])
        else:
            dictBase["prestationForfaitaireProgram"+str(i)] = invoiceElemtListP
            dictBase["prestationPlafonneesProgram"+str(i)] = invoiceElemtListF
            dictBase["prestationsNonMedicalesProgram"+str(i)] = invoiceElemtListS
            dictBase["invoiceElemtTotalProgram"+str(i)] = invoiceElemtTotal
            print(dictBase["invoiceElemtTotalProgram"+str(i)])
        i += 1
    print("invoiceElemtTotal_MontantRecueTotal is ", invoiceElemtTotal_MontantRecueTotal)
    print("invoiceElemtTotal_MtnValideTotal is ", invoiceElemtTotal_MtnValideTotal)
    # dictBase["invoiceElemtTotal"]["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MontantRecueTotal)
    # dictBase["invoiceElemtTotal"]["MtnValideTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MtnValideTotal)
    dictBase["MontnRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MontantRecueTotal)
    dictBase["MtnValideTotal"] =  "{:,.0f}".format(invoiceElemtTotal_MtnValideTotal)
    
    # print(dictBase)

    if location0:
        location0_str = Location.objects.filter(
            code=location0,
            validity_to__isnull=True
            ).first().name
        dictBase["region"] = location0_str

    if location1:
        location1_str = Location.objects.filter(
            code=location1,
            validity_to__isnull=True
            ).first().name
        dictBase["district"] =location1_str
    if location2:
        location2_str = Location.objects.filter(
            code=location2,
            validity_to__isnull=True
            ).first().name
        dictBase["area"] = location2_str
    return dictBase