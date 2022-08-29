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
    for cclaim in claimList:
        claimService = ClaimService.objects.filter(
            claim = cclaim
        )
        for claimServiceElmt in claimService:
            if claimServiceElmt.service.id not in invoiceElemtList[claimServiceElmt.service.packagetype]:
                invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id] = defaultdict(dict)
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["name"] = claimServiceElmt.service.name
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["code"] = claimServiceElmt.service.code
            invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["tarif"] = claimServiceElmt.price_asked
            
            claimServices = ClaimServiceService.objects.filter(
                claimlinkedService = claimServiceElmt
            )
            for claimService in claimServices:
                if type(invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"]) is not dict :
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = claimService.qty_displayed
                else :
                    invoiceElemtList[claimServiceElmt.service.packagetype][claimServiceElmt.service.id]["qty"] = claimService.qty_displayed
            


    print ("{:<5} {:<5} {:<20} {:<10} {:<10} {:<10}".format('type','id','name','Code','tarif','qty'))
    for typeList,v in invoiceElemtList.items():
        for id in  v:
            print("{:<5} {:<5} {:<20} {:<10} {:<10}".format(typeList, id, v[id]['name'], v[id]['code'], v[id]['tarif']))
            #print(v[id]['qty'])
            
    print(invoiceElemtList)

    dictBase =  {
        "data": str(invoiceElemtList),
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

