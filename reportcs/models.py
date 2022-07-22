from uuid import UUID
from django.db import models
from core import models as core_models
from report.services import run_stored_proc_report

def claim_history_query():
    data = run_stored_proc_report(
        "uspSSRSGetClaimHistory"
    )
    return {
        "data": data
    }


def services_performance_query(date_from=None,date_to=None):
    queryset = ()

    return {"data": list(queryset)}


def insuree_without_photo_query(date_from=None,date_to=None):
    queryset = ()

    return {"data": list(queryset)}


def submitted_claim_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def health_facilities_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def feedback_indicators_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def upload_enrolement_from_phone_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def enrolement_officers_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def user_log_report_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

def expired_policies_query():
    data = run_stored_proc_report()
    return {
        "data": data
    }

