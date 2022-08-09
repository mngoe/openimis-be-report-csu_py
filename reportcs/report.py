from distutils.command import upload
from reportcs.models import  assisted_birth_with_cs_query, cesarienne_rate_query, closed_cs_query, complicated_birth_with_cs_query, cpn1_with_cs_query, cs_in_use_query, invoice_per_fosa_query, medium_charge_on_beneficiary_query, mother_cpon_with_cs_query, newborn_cpon_with_cs_query, pregnant_woman_ref_rate_query, pregnant_woman_with_cs_query, sales_objectives_rate_query,periodic_paid_bills_query,periodic_rejected_bills_query,periodic_household_participation_query,new_cs_per_month_query
from reportcs.report_templates import rptSalesRate
from reportcs.report_templates import rptAssistedBirth
from reportcs.report_templates import rptCponUnderCs
from reportcs.report_templates import rptNewbornCPoN
from reportcs.report_templates import rptReferalRate
from reportcs.report_templates import rptCpn4UnderCheck
from reportcs.report_templates import rptCpn1UnderCheck
from reportcs.report_templates import rptInvoicePerFosa
from reportcs.report_templates import rptPaidInvoice
from reportcs.report_templates import rptComplicatedDel
from reportcs.report_templates import rptCesarianRate
from reportcs.report_templates import rptRejectedBills
from reportcs.report_templates import rpthouseholdContribution
from reportcs.report_templates import rptcsInUse
from reportcs.report_templates import rptClosedCs
from reportcs.report_templates import rptBeneficiaryCharge







report_definitions = [ 
    {
        "name": "sales_objectives_rate_report",
        "engine": 0,
        "default_report": rptSalesRate.template ,
        "description": "Achievement rate of sales objectives",
        "module": "reportcs",
        "python_query": sales_objectives_rate_query, 
        "permission": ["131215"],
    },
    {
        "name": "cpn1_under_cs",
        "engine": 0,
        "default_report":rptCpn1UnderCheck.template  ,
        "description": " Number of CPN1 performed under health check ",
        "module": "reportcs",
        "python_query": cpn1_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "cpn4_under_cs",
        "engine": 0,
        "default_report":rptCpn4UnderCheck.template,
        "description": "Number of CPN4 performed under health check ",
        "module": "reportcs",
        "python_query": cpn4_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "assisted_birth_under_cs_report",
        "engine": 0,
        "default_report": rptAssistedBirth.template ,
        "description": "Number of assisted births carried out under health checks ",
        "module": "reportcs",
        "python_query": assisted_birth_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "CPON_under_check_report",
        "engine": 0,
        "default_report": rptCponUnderCs.template  ,
        "description": "Number of CPoN Mother carried out under health check",
        "module": "reportcs",
        "python_query": mother_cpon_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "newborn_CPoN_report",
        "engine": 0,
        "default_report": rptNewbornCPoN.template ,
        "description": "Number of newborn CPoN carried out under health check",
        "module": "reportcs",
        "python_query": newborn_cpon_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "upload_from_phone_report",
        "engine": 0,
        "default_report": rptComplicatedDel.template ,
        "description": "complicated deliveries under CS over a period of time ",
        "module": "reportcs",
        "python_query": complicated_birth_with_cs_query, 
        "permission": ["131215"],
    },
    {
        "name": "enrolement_officers_report",
        "engine": 0,
        "default_report": rptCesarianRate.template,
        "description": "Cesareans rate under CS over a period of time ",
        "module": "reportcs",
        "python_query": cesarienne_rate_query, 
        "permission": ["131215"],
    },
    {
        "name": "pregnant woman reference rate",
        "engine": 0,
        "default_report": rptReferalRate.template ,
        "description": "pregnant woman referal rate ",
        "module": "reportcs",
        "python_query": pregnant_woman_ref_rate_query, 
        "permission": ["131215"],
    },
    {
        "name": "invoice_per_fosa_report",
        "engine": 0,
        "default_report": rptInvoicePerFosa.template ,
        "description": "Referral rate of pregnant women ",
        "module": "reportcs",
        "python_query": invoice_per_fosa_query, 
        "permission": ["131215"],
    },
    {
        "name": "paid_invoice_per_period_report",
        "engine": 0,
        "default_report": rptPaidInvoice.template ,
        "description": "Invoices paid over a period by FOSA ",
        "module": "reportcs",
        "python_query": periodic_paid_bills_query, 
        "permission": ["131215"],
    },
    {
        "name": "rejected_invoice_per_period_report",
        "engine": 0,
        "default_report": rptRejectedBills.template  ,
        "description": "Rejected invoices  over a period by FOSA",
        "module": "reportcs",
        "python_query": periodic_rejected_bills_query, 
        "permission": ["131215"],
    },
    {
        "name": "household_contribution_report",
        "engine": 0,
        "default_report": rpthouseholdContribution.template  ,
        "description": "Household contributions during a given period",
        "module": "reportcs",
        "python_query": periodic_household_participation_query, 
        "permission": ["131215"],
    },
    {
        "name": "household_contribution_report",
        "engine": 0,
        "default_report": rpthouseholdContribution.template  ,
        "description": "New check activated during the month by the HF ",
        "module": "reportcs",
        "python_query": new_cs_per_month_query,
        "permission": ["131215"],
    },
    {
        "name": "check_in_use_report",
        "engine": 0,
        "default_report": rptcsInUse.template  ,
        "description": "Number of CS in use by HF in the month ",
        "module": "reportcs",
        "python_query": cs_in_use_query,
        "permission": ["131215"],
    },
    {
        "name": "closed_check_report",
        "engine": 0,
        "default_report": rptClosedCs.template  ,
        "description": "Closed check in the month ",
        "module": "reportcs",
        "python_query": closed_cs_query,
        "permission": ["131215"],
    },
    {
        "name": "closed_check_report",
        "engine": 0,
        "default_report": rptClosedCs.template  ,
        "description": "Closed check in the month ",
        "module": "reportcs",
        "python_query": closed_cs_query,
        "permission": ["131215"],
    },
            {
        "name": "severe_malaria_cost_report",
        "engine": 0,
        "default_report": rptBeneficiaryCharge ,
        "description": "Average cost of severe malaria charge to insuree",
        "module": "reportcs",
        "python_query": medium_charge_on_beneficiary_query,
        "permission": ["131215"],
    },
    
]