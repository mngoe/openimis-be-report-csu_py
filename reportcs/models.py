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

    claimList = Claim.objects.filter(
        date_from__gte=date_from,
        date_from__lte=date_to
        )
    

    print("Claim")
    invoiceElemtList = defaultdict(dict)
    invoiceElemtTotal = {}
    invoiceElemtTotal["QtyTotal"] = 0
    invoiceElemtTotal["MontantRecueTotal"] = 0
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
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = defaultdict(dict)
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'] = 0
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] = 0
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'] = 0
                
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["name"] = claimServiceElmt.service.name
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["code"] = claimServiceElmt.service.code
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"] = claimServiceElmt.price_asked
            
            if cclaim.status == "16":
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated'] += claimServiceElmt.qty_provided
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum'] += claimServiceElmt.qty_provided * claimServiceElmt.price_asked
                

            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] += claimServiceElmt.qty_provided
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["MontantRecue"] = invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['all'] * invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"]
            if claimServiceElmt.service.packagetype not in invoiceElemtTotal :
                invoiceElemtTotal[claimServiceElmt.service.packagetype] = defaultdict(dict)
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyTotal"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotal"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuated"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValide"] = 0
                invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValide"] = 0

            invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyTotal"] += claimServiceElmt.qty_provided
            print(claimServiceElmt.qty_provided)
            print(invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotal"])
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"QtyValuated"] += invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['valuated']
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValide"] += invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]['sum']
            invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnNotValide"] = invoiceElemtTotal[claimServiceElmt.service.packagetype+"MontantRecueTotal"] - invoiceElemtTotal[claimServiceElmt.service.packagetype+"MtnValide"]
            invoiceElemtTotal["QtyTotal"] += claimServiceElmt.qty_provided

        claimItem = ClaimItem.objects.filter(
            claim = cclaim
        )
        for claimItemElmt in claimItem:
            if claimItemElmt.service.id not in invoiceElemtList[claimItemElmt.service.packagetype]:
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id] = defaultdict(dict)
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"] = defaultdict(dict)
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["all"] = 0
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["valuated"] = 0
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["status"] = 0

            if cclaim.status == "16":
                invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated'] += claimItemElmt.qty_provided

            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["name"] = claimItemElmt.service.name
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["code"] = claimItemElmt.service.code
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"] = claimItemElmt.price_asked
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]["all"] += claimItemElmt.qty_provided
            invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["MontantRecue"] = invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['all'] * invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["tarif"]            
            
            invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyTotal"] += claimItemElmt.qty_provided
            invoiceElemtTotal[claimItemElmt.service.packagetype+"QtyValuated"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['valuated']
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotal"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["MontantRecue"]
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValide"] += invoiceElemtList[claimItemElmt.service.packagetype][claimItemElmt.service.id]["qty"]['sum']
            invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnNotValide"] = invoiceElemtTotal[claimItemElmt.service.packagetype+"MontantRecueTotal"] - invoiceElemtTotal[claimItemElmt.service.packagetype+"MtnValide"]
            
            invoiceElemtTotal["QtyTotal"] += claimItemElmt.qty_provided
        
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
                invoiceElemtTotal["PMontantRecueTotal"] += v[id]['MontantRecue']
                invoiceElemtTotal["PQtyValuated"] += v[id]['qty']['valuated']
                invoiceElemtTotal["PMtnNotValide"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["PMtnValide"] += v[id]['qty']['valuated']


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
                invoiceElemtTotal["FMontantRecueTotal"] = v[id]['MontantRecue']
                invoiceElemtTotal["FQtyValuated"] += v[id]['qty']['valuated']
                invoiceElemtTotal["FMtnNotValide"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["FMtnValide"] += v[id]['qty']['valuated']

            
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
                invoiceElemtTotal["SMontantRecueTotal"] += v[id]['MontantRecue']
                invoiceElemtTotal["SQtyValuated"] += v[id]['qty']['valuated']
                invoiceElemtTotal["SMtnNotValide"] += v[id]['MontantRecue'] - v[id]['tarif']*v[id]['qty']['valuated']
                invoiceElemtTotal["SMtnValide"] += v[id]['qty']['valuated']

            print("{:<5} {:<5} {:<30} {:<10} {:<10} {:<10} {:<10} {:<10}".format(
                typeList, id, v[id]['name'], v[id]['code'], v[id]['tarif'],v[id]['qty']['all'], v[id]['MontantRecue'],v[id]['qty']['valuated']
                ))

    invoiceElemtTotal["FQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["FQtyTotal"])
    invoiceElemtTotal["SQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["SQtyTotal"])
    invoiceElemtTotal["PQtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["PQtyTotal"])
    invoiceElemtTotal["NbFactureValideTotal"] = invoiceElemtTotal["FQtyValuated"] + invoiceElemtTotal["SQtyValuated"] + invoiceElemtTotal["PQtyValuated"]
    invoiceElemtTotal["NbFactureValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["NbFactureValideTotal"])
    invoiceElemtTotal["FQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["FQtyValuated"])
    invoiceElemtTotal["SQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["SQtyValuated"])
    invoiceElemtTotal["PQtyValuated"] = "{:,.0f}".format(invoiceElemtTotal["PQtyValuated"])

    invoiceElemtTotal["MtnValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValide"]+invoiceElemtTotal["SMtnValide"]+invoiceElemtTotal["PMtnValide"])
    invoiceElemtTotal["FMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnValide"])
    invoiceElemtTotal["SMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnValide"])
    invoiceElemtTotal["PMtnValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnValide"])
    invoiceElemtTotal["MtnNonValideTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValide"]+invoiceElemtTotal["SMtnNotValide"]+invoiceElemtTotal["PMtnNotValide"])
    invoiceElemtTotal["FMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["FMtnNotValide"])
    invoiceElemtTotal["SMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["SMtnNotValide"])
    invoiceElemtTotal["PMtnNotValide"] = "{:,.0f}".format(invoiceElemtTotal["PMtnNotValide"])

    invoiceElemtTotal["MontantRecueTotal"] =  "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotal"]+invoiceElemtTotal["FMontantRecueTotal"]+invoiceElemtTotal["SMontantRecueTotal"])

    invoiceElemtTotal["PMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["PMontantRecueTotal"])
    invoiceElemtTotal["SMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["SMontantRecueTotal"])
    invoiceElemtTotal["FMontantRecueTotal"] = "{:,.0f}".format(invoiceElemtTotal["FMontantRecueTotal"])

    invoiceElemtTotal["QtyTotal"] = "{:,.0f}".format(invoiceElemtTotal["QtyTotal"])
    

    print(invoiceElemtTotal)
    dictBase =  {
        "prestationForfaitaire": invoiceElemtListP,
        "prestationPlafonnees": invoiceElemtListF,
        "prestationsNonMedicales": invoiceElemtListS,
        "invoiceElemtTotal" : invoiceElemtTotal,
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

