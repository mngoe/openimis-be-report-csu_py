from distutils.command import upload
from reportcsu.models import invoice_csu_query

from reportcsu.report_templates import rptInvoiceperPeriod

report_definitions = [ 
    {
        "name": "invoice_fosa_csu",
        "engine": 0,
        "default_report":rptInvoiceperPeriod.template,
        "description": "Etat de paiement par fosa",
        "module": "reportcsu",
        "python_query": invoice_csu_query, 
        "permission": ["131215"],
    }
]