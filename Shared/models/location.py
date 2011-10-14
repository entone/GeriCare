import libraries
from system.model import Model
import humongolus.field as field
import views.widget as widget
import humongolus.relationship as relationship
from humongolus.document import Index

class Location(Model):
    
    __db__ = "gericare"
    __collection__ = "locations"
    __dbindexes__ = [Index(field="nursing_home_name"), Index(field="provider_number")]
    __fieldorder__ = ("provider_number", "nursing_home_name", "street", "city", "state", "zip_code", "website", "phone_number", "health_survey_date", 
    "fire_survey_date", "number_of_certified_beds", "percent_of_occupied_beds", "sprinkler_status", "program_participation", "type_of_ownership", "resident_and_family_councils", 
    "located_within_a_hospital_", "multi_nursing_home_ownership_", "continuing_care_retirement_community_", 
    "quality_indicator_survey_", "special_focus_facility_")
    
    
    provider_number = field.Char(label="Provider Number", disabled=True)
    nursing_home_name = field.Char(label="Name")
    street = field.Char(label="Street")
    city = field.Char(label="City")
    state = field.Char(label="State")
    zip_code = field.Char(label="Zip Code")
    website = field.Char(label="Website")
    phone_number = field.Char(label="Phone Number")
    health_survey_date = field.Date(label="Health Survey", widget=widget.DateCtrl)
    fire_survey_date = field.Date(label="Fire Survey", widget=widget.DateCtrl)
    number_of_certified_beds = field.Integer(label="Number of Beds")
    total_number_of_residents = field.Integer(label="Number of Residents")
    percent_of_occupied_beds = field.Integer(label="Percent Occupied")
    sprinkler_status = field.Char(label="Sprinkler Status")
    program_participation = field.Char(label="Program Participation")
    type_of_ownership = field.Char(label="Type of Ownership")
    resident_and_family_councils = field.Char(label="Resident and Family Council")
    located_within_a_hospital_ = field.Boolean(label="In Hospital?")
    multi_nursing_home_ownership_ = field.Boolean(label="Multi Nursing Home Ownership?")
    continuing_care_retirement_community_ = field.Boolean(label="Continuing Care Retirement Community")
    quality_indicator_survey_ = field.Boolean(label="Quality Indicator Survey?")
    special_focus_facility_ = field.Boolean(label="Special Focus Facility")
    
    
    
