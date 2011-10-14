import time
from system.controller import Controller
from models.location import Location
from models.deficiency import Deficiency
from models.enforcement import Enforcement
from views.location import *
from pymongo.objectid import ObjectId
from system.jsonobject import JSONObject
import system.util as util

class Locations(Controller):
    
    class Meta:
        db = 'gericare'
        collection = 'locations'
        fields = ['nursing_home_name', 'provider_id', 'city', 'state']
        table_template = '/locations/table.html'
        template = '/locations/all.html'
        cls = Location
        view = LocationTable
        form = LocationForm
        new_form = LocationNewForm
    
    def get_all(self):
        self.Meta.cls.__currentview__ = self.Meta.view
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find(query={"city":"Chicago"}).sort("nursing_home_name", 1), 'columns':columns}
        return JSONObject(success=True, html=self.render(self.Meta.table_template, args), action='replace')
    
    def index(self): return self.show_all()
    
    #@permissions(level=9)
    def show_all(self):
        self.Meta.cls.__currentview__ = self.Meta.view
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find(query={"city":"Chicago"}).sort("nursing_home_name", 1), 'columns':columns}
        return self.render(self.Meta.template, args)
        
    def search(self, query=None):
        self.Meta.cls.__currentview__ = self.Meta.view
        qu = self.compile_query(query)
        qu['city'] = "Chicago"       
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find(qu).sort("_id", -1), 'columns':columns}
        return JSONObject(success=True, html=self.render(self.Meta.table_template, args))
        
    def load_changelog(self, id):
        collection = self.admin_db['change_log']
        query = {"reference.id":ObjectId(id)}
        changes = collection.find(query).sort('when', -1).limit(100)
        _changes = []
        for t in changes:
            t['user'] = self.admin_db['users'].find_one({'_id':t['user']})
            _changes.append(t)
        return JSONObject(success=True, data=changes, html=self.render('models/location/changelog.html', {'changes':_changes}))
        
    def update_names(self):
        for loc in Location.find():
            loc.nursing_home_name = util.unescape(loc.nursing_home_name)
            loc.save()
        
        
        return u"Success!"
        
    def tab_details(self, id):
        ob = Location(id=id)
        return JSONObject(success=True, html=ob.render_form())
        
    def tab_enforcements(self, id):
        ob = Location(id=id)
        return JSONObject(success=True, html=self.render("models/location/enforcements.html", args={"location":ob}))
        
    def tab_deficiencies(self, id):
        ob = Location(id=id)
        return JSONObject(success=True, html=self.render("models/location/deficiencies.html", args={"location":ob}))
    
    
