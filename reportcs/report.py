from distutils.command import upload
from reportcs.models import claim_history_query, enrolement_officers_query, expired_policies_query, feedback_indicators_query, health_facilities_query, insuree_without_photo_query, services_performance_query, submitted_claim_query, upload_enrolement_from_phone_query, user_log_report_query
from reportcs.report_templates import rptClaimHistory
from reportcs.report_templates import rptEnrolementOfficers
from reportcs.report_templates import rptExpiredPolicies
from reportcs.report_templates import rptFeedbackIndicators
from reportcs.report_templates import rptHealthFacilities
from reportcs.report_templates import rptServicePerformance
from reportcs.report_templates import rptInsureeWithoutPhoto
from reportcs.report_templates import rptSubmittedClaim
from reportcs.report_templates import rptUserLogReport
from reportcs.report_templates import rptUploadFromPhone


report_definitions = [ 
    {
        "name": "claim_history_report",
        "engine": 0,
        "default_report": rptClaimHistory.template ,
        "description": "claim history report sample",
        "module": "reportcs",
        "python_query": claim_history_query, 
        "permission": ["131215"],
    },
    {
        "name": "performance_service_report",
        "engine": 0,
        "default_report": rptServicePerformance.template ,
        "description": " service performance report sample",
        "module": "reportcs",
        "python_query": services_performance_query, 
        "permission": ["131215"],
    },
    {
        "name": "insuree_without_photo_report",
        "engine": 0,
        "default_report": rptInsureeWithoutPhoto.template ,
        "description": "insuree without photo report sample",
        "module": "reportcs",
        "python_query": insuree_without_photo_query, 
        "permission": ["131215"],
    },
    {
        "name": "submitted_claim_report",
        "engine": 0,
        "default_report": rptSubmittedClaim.template ,
        "description": "submitted claim report sample",
        "module": "reportcs",
        "python_query": submitted_claim_query, 
        "permission": ["131215"],
    },
    {
        "name": "health_facilities_report",
        "engine": 0,
        "default_report": rptHealthFacilities.template ,
        "description": "health facilities report sample",
        "module": "reportcs",
        "python_query": health_facilities_query, 
        "permission": ["131215"],
    },
    {
        "name": "feedback_indicators_report",
        "engine": 0,
        "default_report": rptFeedbackIndicators.template ,
        "description": "feedback indicators report sample",
        "module": "reportcs",
        "python_query": feedback_indicators_query, 
        "permission": ["131215"],
    },
    {
        "name": "upload_from_phone_report",
        "engine": 0,
        "default_report": rptUploadFromPhone.template ,
        "description": "upload from phone report sample",
        "module": "reportcs",
        "python_query": upload_enrolement_from_phone_query, 
        "permission": ["131215"],
    },
    {
        "name": "enrolement_officers_report",
        "engine": 0,
        "default_report": rptEnrolementOfficers.template ,
        "description": "enrolement officers report sample",
        "module": "reportcs",
        "python_query": enrolement_officers_query, 
        "permission": ["131215"],
    },
    {
        "name": "user_log_report",
        "engine": 0,
        "default_report": rptUserLogReport.template ,
        "description": "user log report sample",
        "module": "reportcs",
        "python_query": user_log_report_query, 
        "permission": ["131215"],
    },
    {
        "name": "expired_policies_report",
        "engine": 0,
        "default_report": rptExpiredPolicies.template ,
        "description": "expired policies report sample",
        "module": "reportcs",
        "python_query": expired_policies_query, 
        "permission": ["131215"],
    },
    
]