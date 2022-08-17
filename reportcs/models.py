from django.db import models
from core import models as core_models
from report.services import run_stored_proc_report
from claim.models import Claim
import datetime


def cpn1_with_cs_query(user, **kwargs):
    date_from = kwargs.get("dateFrom")
    format = "%Y-%m-%d"
    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")
    date_to = kwargs.get("dateTo")
    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")

    queryset = Claim.objects.filter(validity_from__gte=date_from, validity_to__gte=date_to, code='CPN1').count()
    return {
        "data": str(queryset),
        "dateFrom": date_from_str,
        "dateTo": date_to_str
        }

def cpn4_with_cs_query(date_from=None, date_to=None, **kwargs):
    date_from = kwargs.get("dateFrom")
    format = "%Y-%m-%d"
    date_from_object = datetime.datetime.strptime(date_from, format)
    date_from_str = date_from_object.strftime("%d/%m/%Y")
    date_to = kwargs.get("dateTo")
    date_to_object = datetime.datetime.strptime(date_to, format)
    date_to_str = date_to_object.strftime("%d/%m/%Y")

    queryset = Claim.objects.filter(validity_from__gte=date_from, validity_to__gte=date_to, code='CPN1').count()
    return {
        "data": str(queryset),
        "dateFrom": date_from_str,
        "dateTo": date_to_str
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

