from django.db import models
from core import models as core_models
from report.services import run_stored_proc_report


def cpn1_with_cs_query(date_from=None,date_to=None):
    queryset = ()
    return {"data": list(queryset)}

def cpn4_with_cs_query(date_from=None,date_to=None):
    queryset = ()
    return {"data": list(queryset)}

def assisted_birth_with_cs_query(date_from=None,date_to=None):
    queryset = ()
    return {"data": list(queryset)}

def mother_cpon_with_cs_query():
    queryset = ()
    return {"data": list(queryset)}

def newborn_cpon_with_cs_query():
    queryset = ()
    return {"data": list(queryset)}

def complicated_birth_with_cs_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def cesarienne_rate_query():
    queryset = ()
    return {"data": list(queryset)}

def pregnant_woman_ref_rate_query():
    queryset = ()
    return {"data": list(queryset)}

def user_log_report_query(user,date_from=None, date_to=None,action=None):
    data = run_stored_proc_report(
        "uspSSRSUserLogReport",
        FromDate = date_from,
        ToDate  = date_to,
        Action = action,
    )
    return {
        "data": data
    }

def invoice_per_fosa_query():
    queryset = ()
    return {"data": list(queryset)}

def expired_policies_query():
    queryset = ()
    return {"data": list(queryset)}

def periodic_paid_bills_query():
    queryset = ()
    return {"data": list(queryset)}

def periodic_rejected_bills_query():
    queryset = ()
    return {"data": list(queryset)}

def periodic_household_participation_query():
    queryset = ()
    return {"data": list(queryset)}

def cs_sales_amount_query():
    queryset = ()
    return {"data": list(queryset)}

def new_cs_per_month_query():
    queryset = ()
    return {"data": list(queryset)}

def cs_in_use_query():
    queryset = ()
    return {"data": list(queryset)}

def closed_cs_query():
    queryset = ()
    return {"data": list(queryset)}

def severe_malaria_cost_query():
    queryset = ()
    return {"data": list(queryset)}

