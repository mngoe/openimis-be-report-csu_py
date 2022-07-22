from uuid import UUID
from django.db import models
from core import models as core_models

# Create your models here.
class TestReport(core_models.UUIDModel):
    """ Model test"""
    REPORT_BRO = 0
    REPORT_ENGINE_CHOICES = (
        (REPORT_BRO, "Report Bro - PDF"),
    )
    #name = models.CharField(max_length=255, blank=False, null=False, unique=True)
    #engine = models.IntegerField( choices=REPORT_ENGINE_CHOICES, default=REPORT_BRO)
    RoleId =  models.IntegerField(null=False)
    RoleName = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = "tblRole"

#fonction 

# def test_portdata_query(user,date_from=None, date_to=None, **kwargs):
#     if date_from:
#         filters &= Q(validity_from__gte=date_from)

#     queryset = (
#         Insuree.objects.filter(filters).values(
#             "","","",enroll_date=F(""),
#         )
#     )

#     return {"data": list(queryset)}