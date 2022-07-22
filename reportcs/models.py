from uuid import UUID
from django.db import models
from core import models as core_models

# Create your models here.
class TestReport(core_models.UUIDModel):
    """ Model test """
    
