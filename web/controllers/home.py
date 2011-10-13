from system.controller import Controller
from models.location import Location
from system.jsonobject import JSONObject

class Home(Controller):
    
    def index(self, start=0, limit=10): 
        return self.render("main.html") 
        
    def page(self, start, limit=10):
        locations = Location.find(query={"city":"Chicago"}).skip(int(start)).limit(int(limit)).sort("nursing_home_name", 1)
        return JSONObject(success=True, action="replace", html=self.render("locations.html", args={"locations":locations}), identifier="#locations", data={"next":start})
