from tokenize import String
from django.db import models
from core import models as core_models
from report.services import run_stored_proc_report
from claim.models import Claim, ClaimService, ClaimItem, ClaimServiceService
from location.models import Location, HealthFacility
from collections import defaultdict

import json
import datetime

def invoice_cs_query(user, **kwargs):
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

    dictBase =  {
        "dateFrom": date_from_str,
        "dateTo": date_to_str,
        "prestationForfaitaire" : [],
        "prestationPlafonnees" : [],
        "prestationsNonMedicales" : [],
        "invoiceElemtTotal": []
        }

    dictGeo = {}
    if hflocation and hflocation!="0" :
        hflocationObj = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first()
        dictBase["fosa"] = hflocationObj.name
        dictGeo['health_facility'] = hflocationObj.id
    

    claimList = Claim.objects.filter(
        date_from__gte=date_from,
        date_from__lte=date_to,
        **dictGeo
        )

    invoiceElemtList = defaultdict(dict)
    invoiceElemtTotal = defaultdict(int)
    invoiceElemtListP = []
    invoiceElemtListF = []
    invoiceElemtListS = []

    for cclaim in claimList:
        claimService = ClaimService.objects.filter(
            claim = cclaim
        )
        for claimServiceElmt in claimService:
            if claimServiceElmt.service.id not in invoiceElemtList[claimServiceElmt.service.packagetype]:
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id] = defaultdict(dict)
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = defaultdict(int)

            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["name"] = claimServiceElmt.service.name
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["code"] = claimServiceElmt.service.code
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"] = claimServiceElmt.price_asked
            
            if cclaim.status == "16":
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'] += int(claimServiceElmt.qty_provided)
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'] += (claimServiceElmt.qty_provided * claimServiceElmt.price_asked)
                

            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] += claimServiceElmt.qty_provided
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] = invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] * invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"]
            if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
                invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(int)

            if isinstance(invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"], str):
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuated"])

            if isinstance(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"], str):
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValide"])

            if isinstance(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValideV"], str):
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValideV"] = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValide"])

            invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyTotalV"] += int(claimServiceElmt.qty_provided)
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuatedV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'])
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"] += int(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'])
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValideV"] = int(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotalV"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValideV"])
            invoiceElemtTotal["QtyTotalV"] += int(claimServiceElmt.qty_provided)

        claimItem = ClaimItem.objects.filter(
            claim = cclaim
        )
        for claimItemElmt in claimItem:
            if claimItemElmt.service.id not in invoiceElemtList[claimItemElmt.service.packagetype]:
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id] = defaultdict(int)

            if cclaim.status == "16":
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated'] += claimItemElmt.qty_provided

            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["name"] = claimItemElmt.service.name
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["code"] = claimItemElmt.service.code
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"] = claimItemElmt.price_asked
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["all"] += claimItemElmt.qty_provided
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["MontantRecue"] = invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['all'] * invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"]            
            
            if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
                invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(int)

            invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyTotalV"] += claimItemElmt.qty_provided
            invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyValuatedV"] += int(invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated'])
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotalV"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["MontantRecue"]
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValideV"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['sum']
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnNotValideV"] = invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotal"] - invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValide"]
            
            invoiceElemtTotal["QtyTotalV"] += claimItemElmt.qty_provided
        
    print ("{:<5} {:<5} {:<30} {:<10} {:<10} {:<10} {:<10}".format('type','id','name','Code','tarif','qty', 'Montant Recus'))
    for typeList,v in invoiceElemtList.items():
        for id in  v:
            if typeList=="P":
                invoiceElemtListP.append(dict(
                    name=v[id]['name'],
                    code=v[id]['code'],
                    tarif=str("{:,.0f}".format(v[id]['tarif'])),
                    nbrFacture = str(v[id]['qty']['all']),
                    mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                    nbFactureValides= str(v[id]['qty']['valuated']),
                    montantNonValide = str("{:,.0f}".format(v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated'])),
                    montantValide =  str("{:,.0f}".format(v[id]['tarif']*v[id]['qty']['valuated']))
                    ))
                invoiceElemtTotal["PMontantRecueTotalV"] += v[id]['MontantRecue']
                invoiceElemtTotal["PQtyValuatedV"] += v[id]['qty']['valuated']
                invoiceElemtTotal["PMtnNotValideV"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["PMtnValideV"] += v[id]['qty']['valuated']


            if typeList=="F":
                invoiceElemtListF.append(dict(
                    name=v[id]['name'],
                    code=v[id]['code'],
                    tarif=str("{:,.0f}".format(v[id]['tarif'])),
                    nbrFacture = str(v[id]['qty']['all']),
                    mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                    nbFactureValides= str(v[id]['qty']['valuated']),
                    montantNonValide = str("{:,.0f}".format(v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated'])),
                    montantValide =  str("{:,.0f}".format(v[id]['tarif']*v[id]['qty']['valuated']))                    
                    ))
                invoiceElemtTotal["FMontantRecueTotalV"] += v[id]['MontantRecue']
                invoiceElemtTotal["FQtyValuatedV"] += v[id]['qty']['valuated']
                invoiceElemtTotal["FMtnNotValideV"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["FMtnValideV"] += v[id]['qty']['valuated']

            
            if typeList=="S":
                invoiceElemtListS.append(dict(
                    name=v[id]['name'],
                    code=v[id]['code'],
                    tarif=str("{:,.0f}".format(v[id]['tarif'])),
                    nbrFacture = str(v[id]['qty']['all']),
                    mtnFactureRecues= str("{:,.0f}".format(v[id]['MontantRecue'])),
                    nbFactureValides= str(v[id]['qty']['valuated']),
                    montantNonValide = str("{:,.0f}".format(v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated'])),
                    montantValide =  str("{:,.0f}".format(v[id]['tarif']*v[id]['qty']['valuated']))
                    ))
                invoiceElemtTotal["SMontantRecueTotalV"] += v[id]['MontantRecue']
                invoiceElemtTotal["SQtyValuatedV"] += v[id]['qty']['valuated']
                invoiceElemtTotal["SMtnNotValideV"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["SMtnValideV"] += v[id]['qty']['valuated']

            print("{:<5} {:<5} {:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                typeList, id, v[id]['name'], v[id]['code'], v[id]['tarif'],v[id]['qty']['all'], v[id]['MontantRecue'],v[id]['qty']['valuated']
                ))


    invoiceElemtTotal["NbFactureValideTotal"] = invoiceElemtTotal["FQtyValuatedV"] + invoiceElemtTotal["SQtyValuatedV"] + invoiceElemtTotal["PQtyValuatedV"]
    invoiceElemtTotal["NbFactureValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["NbFactureValideTotalV"])
    invoiceElemtTotal["FQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["FQtyValuatedV"])
    invoiceElemtTotal["SQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["SQtyValuatedV"])
    invoiceElemtTotal["PQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["PQtyValuatedV"])

    invoiceElemtTotal["MtnValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"]+invoiceElemtTotal["SMtnValideV"]+invoiceElemtTotal["PMtnValideV"])
    invoiceElemtTotal["FMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValideV"])
    invoiceElemtTotal["SMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnValideV"])
    invoiceElemtTotal["PMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnValideV"])
    invoiceElemtTotal["MtnNonValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"]+invoiceElemtTotal["SMtnNotValideV"]+invoiceElemtTotal["PMtnNotValideV"])
    invoiceElemtTotal["FMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValideV"])
    invoiceElemtTotal["SMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnNotValideV"])
    invoiceElemtTotal["PMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnNotValideV"])

    invoiceElemtTotal["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"]+invoiceElemtTotal["FMontantRecueTotalV"]+invoiceElemtTotal["SMontantRecueTotalV"])
    invoiceElemtTotal["PMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotalV"])
    invoiceElemtTotal["SMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["SMontantRecueTotalV"])
    invoiceElemtTotal["FMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMontantRecueTotalV"])

    invoiceElemtTotal["QtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["QtyTotalV"])
    

    dictBase["prestationForfaitaire"] = invoiceElemtListP
    dictBase["prestationPlafonnees"] = invoiceElemtListF
    dictBase["prestationsNonMedicales"] = invoiceElemtListS
    dictBase["invoiceElemtTotal"] = invoiceElemtTotal

    print(dictBase)

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

def cpn1_with_cs_query(user, **kwargs):
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

    queryset = Claim.objects.filter(
        validity_from__gte=date_from,
        validity_to__gte=date_to,
        code='CPN1'
        ).count()

    dictBase =  {
        "data": str(queryset),
        "dateFrom": date_from_str,
        "dateTo": date_to_str
        }
    print(dictBase)

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
    
    if hflocation:
        hflocation_str = HealthFacility.objects.filter(
            code=hflocation,
            validity_to__isnull=True
            ).first().name
        dictBase["fosa"] = hflocation_str
    return dictBase

def cpn4_with_cs_query(user, **kwargs):
    date_from = kwargs.get("dateFrom")
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

    queryset = Claim.objects.filter(
        validity_from__gte=date_from,
        validity_to__gte=date_to,
        code='CPN4'
        ).count()
    return {
        "data": str(queryset),
        "dateFrom": date_from_str,
        "dateTo": date_to_str,
        "region": location0,
        "district": location1,
        "area": location2,
        "fosa": hflocation
        }

def assisted_birth_with_cs_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def mother_cpon_with_cs_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def newborn_cpon_with_cs_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def complicated_birth_with_cs_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def cesarienne_rate_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def pregnant_woman_ref_rate_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def invoice_per_fosa_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def expired_policies_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def periodic_paid_bills_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def periodic_rejected_bills_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def periodic_household_participation_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def cs_sales_amount_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def new_cs_per_month_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def cs_in_use_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def closed_cs_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

def severe_malaria_cost_query(date_from=None, date_to=None, **kwargs):
    queryset = ()
    return {"data": list(queryset)}

