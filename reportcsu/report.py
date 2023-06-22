from distutils.command import upload
from reportcsu.models import invoice_csu_query, invoice_hiv_query

from reportcsu.report_templates import rptInvoicePerFosa, rptInvoiceReportHIV

report_definitions = [ 
    {
        "name": "invoice_fosa_csu",
        "engine": 0,
        "default_report": rptInvoicePerFosa.template,
        "description": "Etat de paiement par fosa CSU",
        "module": "reportcsu",
        "python_query": invoice_csu_query, 
        "permission": ["131215"],
    },
    {
        "name": "invoice_hiv",
        "engine": 0,
        "default_report":rptInvoiceReportHIV.template,
        "description": "Etat de paiement HIV",
        "module": "reportcsu",
        "python_query": invoice_hiv_query, 
        "permission": ["131215"],
    }
]