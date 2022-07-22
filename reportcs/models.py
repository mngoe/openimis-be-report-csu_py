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


# # Create your models here.
# class TestReport(core_models.UUIDModel):
#     """ Model test """
    
