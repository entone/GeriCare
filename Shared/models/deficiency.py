import libraries
from system.model import Model
from models.location import Location
import humongolus.field as field
import views.widget as widget
import humongolus.relationship as relationship
from humongolus.document import Index

class Deficiency(Model):
    
    __db__ = "gericare"
    __collection__ = "deficiencies"
    __dbindexes__ = [Index(name="location", field="location")]
    __fieldorder__ = ("deficiency_type", "deficiency_category", "definciency", "survey_date", "date_of_correction", "level_of_harm", "scope")
    
    
    deficiency_type = field.Char(label="Type", disabled=True)
    deficiency_category = field.Char(label="Category", disabled=True)
    deficiency = field.Char(label="Definciency", disabled=True)
    survey_date = field.Date(label="Survey Date", disabled=True)
    date_of_correction = field.Date(label="Date of Correction", disabled=True)
    level_of_harm = field.Char(label="Level of Harm", disabled=True)
    scope = field.Char(label="Scope", disabled=True)
    location = field.MongoId(type=Location)
    
    
Location.deficiencies = relationship.Lazy(type=Deficiency, key="location")
