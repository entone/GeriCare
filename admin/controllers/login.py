from system.controller import Controller

class Login(Controller):    
    def login(self): 
        return self.render('login.html')