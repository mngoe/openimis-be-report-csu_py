import io
import json
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseServerError, FileResponse
from reportbro import Report, ReportBroError
from .models import TestReport
from .test_report import test_report
from django.core.serializers.json import DjangoJSONEncoder


class ReportService(object):

    def __init__(self, user):
        self.user = user

    def process(self, report, data, default=None):
        try:
            r = TestReport.objects.get(name=report).definition
        except ObjectDoesNotExist:
            if default:
                r = default
            else:
                r = test_report
                data = {
                    "report_name": report,
                    "data_dump": json.dumps(data, cls=DjangoJSONEncoder)
                }

        r = Report(json.loads(r), data)
        if r.errors:
            raise ReportBroError(r.errors[0])
        pdf_report = r.generate_pdf()
        return FileResponse(
            io.BytesIO(pdf_report),
            as_attachment=False
        )
