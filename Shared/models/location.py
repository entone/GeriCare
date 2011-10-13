import libraries
from system.model import Model
import humongolus.field as field
import humongolus.relationship as relationship

class Location(Model):
    
    __db__ = "gericare"
    __collection__ = "locations"
    
    provider_number = field.Char(label="Provider Number")
    nursing_home_name = field.Char(label="Name")
    street = field.Char(label="Street")
    city = field.Char(label="City")
    state = field.Char(label="State")
    zip_code = field.Char(label="Zip Code")
    phone_number = field.Char(label="Phone Number")
    health_survey_date = field.Date(label="Health Survey")
    fire_survey_date = field.Date(label="Fire Survey")
    number_of_certified_beds = field.Integer(label="Number of Beds")
    total_number_of_residents = field.Integer(label="Number of Residents")
    percent_of_occupied_beds = field.Integer(label="Percent Occupied")
    sprinkler_status = field.Char(label="Sprinkler Status")
    program_participation = field.Char(label="Program Participation")
    type_of_ownership = field.Char(label="Type of Ownership")
    located_within_a_hospital_ = field.Boolean(label="In Hospital?")
    multi_nursing_home_ownership_ = field.Boolean(label="Multi Nursing Home Ownership?")
    resident_and_family_councils = field.Char(label="Resident and Family Council")
    continuing_care_retirement_community_ = field.Boolean(label="Continuing Care Retirement Community")
    quality_indicator_survey_ = field.Boolean(label="Quality Indicator Survey?")
    special_focus_facility_ = field.Boolean(label="Special Focus Facility")
    
    
    
