import imp
from reportcs.models import claim_history_query
from reportcs import claim_history_report


report_definitions = [ 
    {
        "name": "claim_history_report",
        "engine": 0,
        "default_report": claim_history_report.template ,
        "description": "claim history report sample",
        "module": "reportcs",
        "python_query": claim_history_query, 
        "permission": ["131215"],
    },
    
]