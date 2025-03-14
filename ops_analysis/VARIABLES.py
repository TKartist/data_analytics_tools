FILTERS = {
    "appeal_code__start_date__lte" : "date_lte",
    "appeal_code__start_date__gte" : "date_gte",
    "type_validated__in" : "type_val",
    "sector_validated__in" : "sec_val",
    "appeal_code__dtype__in" : "dtype",
    "appeal_code__region" : "region",
    "search_extracts" : "search",
    "appeal_code__country__in" : "country",
    "organization_validated__in" : "org_val",
    "per_component_validated__in" : "per_comp",
}

SECTORS = ["WASH", "PGI", "CEA", "Migration", "Health (Public)",  "DRR", "Shelter", "NS Strengthening", "Education", "Livelihoods", "Recovery", "Internal Displacement", "Health (Clinical)", "COVID-19"]
REGIONS = ["Africa", "Americas", "Asia Pacific", "Europe", "Middle East & North Africa"]