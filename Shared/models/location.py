import libraries
from system.model import Model, EmbeddedModel
import humongolus.field as field
import views.widget as g_widget
import humongolus.widget as widget
import humongolus.relationship as relationship
from humongolus.document import Index

class Staff(EmbeddedModel):
    __fieldorder__ = ("number_of_residents", "number_of_rn_hours_per_resident_per_day", "number_of_lpn_lvn_hours_per_resident_per_day", 
            "total_number_of_licensed_staff_hours_per_resident_per_day", "number_of_cna_hours_per_resident_per_day")
            
    number_of_residents = field.Integer(label="Residents", disabled=True)
    number_of_rn_hours_per_resident_per_day = field.Float(label="RN Hours per Resident per Day", disabled=True)
    number_of_lpn_lvn_hours_per_resident_per_day = field.Float(label="LVN Hours per Resident per Day", disabled=True) 
    total_number_of_licensed_staff_hours_per_resident_per_day = field.Float(label="Licensed Staff Hours per Resident per Day", disabled=True)
    number_of_cna_hours_per_resident_per_day = field.Float(label="CNA Hours per Resident per Day", disabled=True)
    
    
class Ratings(EmbeddedModel):
    __fieldorder__ = ("overall_star_rating", "rn_only_star_rating", "quality_measures_star_rating", "health_inspections_star_rating", "nurse_staffing_star_rating")
    
    overall_star_rating = field.Integer(label="Overall", disabled=True)
    rn_only_star_rating = field.Integer(label="RN", disabled=True)
    quality_measures_star_rating = field.Integer(label="Quality Measures", disabled=True)
    health_inspections_star_rating = field.Integer(label="Health Inspections", disabled=True)
    nurse_staffing_star_rating  = field.Integer(label="Nurse Staffing", disabled=True)


class Location(Model):
    
    __db__ = "gericare"
    __collection__ = "locations"
    __dbindexes__ = [Index(name="name", field="nursing_home_name"), Index(name="provider_number", field="provider_number")]
    __fieldorder__ = ("provider_number", "nursing_home_name", "street", "city", "state", "zip_code", "website", "phone_number", "health_survey_date", 
    "fire_survey_date", "number_of_certified_beds", "percent_of_occupied_beds", "sprinkler_status", "program_participation", "type_of_ownership", "resident_and_family_councils",
    "ratings", "staffing", 
    "located_within_a_hospital_", "multi_nursing_home_ownership_", "continuing_care_retirement_community_", 
    "quality_indicator_survey_", "special_focus_facility_")
    
    
    provider_number = field.Char(label="Provider Number", disabled=True)
    nursing_home_name = field.Char(label="Name")
    street = field.Char(label="Street")
    city = field.Char(label="City")
    state = field.Char(label="State")
    zip_code = field.Char(label="Zip Code")
    website = field.Char(label="Website", widget=widget.Link)
    phone_number = field.Char(label="Phone Number")
    health_survey_date = field.Date(label="Health Survey", disabled=True)
    ratings = Ratings()
    staffing = Staff()
    
    fire_survey_date = field.Date(label="Fire Survey", disabled=True)
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
    
    
    
