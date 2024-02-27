from distutils.command import upload
from reportcsu.models import invoice_csu_query, invoice_hiv_query,\
    invoice_declaration_naissance_query, invoice_fagep_query

from reportcsu.report_templates import rptInvoicePerFosa,\
    rptInvoiceReportHIV, rptInvoiceDnPerFosa, rptInvoiceFagPerFosa

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
        "name": "invoice_fosa_DNBD",
        "engine": 0,
        "default_report": rptInvoiceFagPerFosa.template,
        "description": "Etat de paiement par fosa FAGEP",
        "module": "reportcsu",
        "python_query": invoice_fagep_query, 
        "permission": ["131215"],
    },
]