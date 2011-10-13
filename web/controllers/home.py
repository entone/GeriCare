from system.controller import Controller

class Home(Controller):
    
    def index(self, *args, **kwargs): return self.render("main.html", args=kwargs) 
