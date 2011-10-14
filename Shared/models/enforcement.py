import libraries
from system.model import Model
from models.location import Location
import humongolus.field as field
import views.widget as widget
import humongolus.relationship as relationship
from humongolus.document import Index

class Enforcement(Model):
    __db__ = "gericare"
    __collection__ = "enforements"
    __dbindexes__ = [Index(name="location", field="location")]
    __fieldorder__ = ("enforement_type", "civil_money_penalty", "survey_date")
    
    
    enforcement_type = field.Char(label="Type", disabled=True)
    civil_money_penalty = field.Char(label="Penalty", disabled=True)
    survey_date = field.Date(label="Survey Date", disabled=True)
    location = field.MongoId(type=Location)
    
Location.enforcements = relationship.Lazy(type=Enforcement, key="location")
