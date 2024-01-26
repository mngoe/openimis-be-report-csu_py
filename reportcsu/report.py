from distutils.command import upload
from reportcsu.models import invoice_csu_query, invoice_hiv_query, invoice_declaration_naissance_query, invoice_district_query

from reportcsu.report_templates import rptInvoicePerFosa, rptInvoiceReportHIV, rptInvoiceDnPerFosa, rptInvoiceDistrictPerFosa

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
    },
    {
        "name": "invoice_fosa_DNBD",
        "engine": 0,
        "default_report": rptInvoiceDnPerFosa.template,
        "description": "Etat de paiement par fosa Declaration Naissance",
        "module": "reportcsu",
        "python_query": invoice_declaration_naissance_query, 
        "permission": ["131215"],
    },
    {
        "name": "invoice_district_csu",
        "engine": 0,
        "default_report": rptInvoiceDistrictPerFosa.template,
        "description": "Etat de paiement par District",
        "module": "reportcsu",
        "python_query": invoice_district_query, 
        "permission": ["131215"],
    },
]