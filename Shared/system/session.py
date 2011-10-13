import settings
import datetime
import system.util as util
from system.model import Model
import libraries
import humongolus.field as field
from pymongo.objectid import ObjectId
from system.user import User

class Session(Model):
    
    __db__ = 'hotspot'
    __collection__ = 'sessions'
    
    user = field.MongoId(type=User, label='User')
    created = field.Date(label='Created')
    last_active = field.Date(label='Updated')
    
    logged_in = False
    
    def __init__(self, **kwargs):
        super(Session, self).__init__(**kwargs)
        self.logger.debug("INIT")
        self.logger.debug(kwargs)
        if self.__id__: 
            self.logger.debug("hmm, session valid")
            self.update_session()
    
    def login(self, username, password):
        self.logger.debug("LOGIN")
        users = User.find({'username':username})
        if users.count():
            for user in users:
                valid = user.check_password(password)
                self.logger.debug("VALID: %s" % valid)
                if valid and user.status == 'Active':
                    self.user = user.__id__
                    return self.create_session()
        return False
            
    def create_session(self):
        self.logger.debug("CREATE")
        self.created = datetime.datetime.utcnow()
        self.logger.debug("Session Created %s" % self.created)
        return self.update_session()
    
    def update_session(self):
        try:
            self.logger.debug("UPDATE")
            self.logger.debug(self.user)
            self.last_active = datetime.datetime.utcnow()
            if self.save():
                self.logger.debug("SAVED! %s" % self.__id__)
                self.logged_in = True
                return self.logged_in
        except Exception as e: 
            self.logger.exception(e)
            pass
        return False
    
    
        
