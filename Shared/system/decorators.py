class permissions(object):
    def __init__(self, level=0):
        self.level = level
    
    def allowed(self, cls):
        return self.check_session(cls.session)
    
    def check_session(self, session):
        if session.user.allowed(self.level): return True
        else: raise Exception("You do not have proper permissions to exceute this action")
    
    def __call__(self, f):        
        def wrapper(cls, *args, **kwargs):
            if self.check_session(cls.session): return f(cls, *args, **kwargs)
        return wrapper
        
        
        
def singleton(cls):
    instances = {}
    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance
