from system.model import Model
import libraries
import humongolus.relationship as relationship
import humongolus.field as field
import humongolus.widget as widget
from system.usergroup import UserGroup
import settings
import random, hashlib
from system.jsonobject import JSONObject

class User(Model):
    __db__ = settings.ADMIN_DB
    __collection__ = "users"
    
    __fieldorder__ = ('firstName', 'lastName', 'email', 'status', 'username', 'password')
    
    firstName = field.Char(required=True, label="First Name")
    lastName = field.Char(required=True, label="Last Name")
    email = field.Email(label="Email")
    status = field.Choice(required=True, label="Status", choices=['Active', 'Hold', 'Inactive', 'Suspended'], widget=widget.Select)
    username = field.Char(required=True, label="Username")
    password = field.Password(required=False, label="Password", widget=widget.ConfirmPassword)
    
    #groups = relationship.List(type=UserGroup)
    
    def init(self, *args, **kwargs):pass
    
    def allowed(self, level):
        for group in self.groups:
            if group.level >= level: return True
        return False
    
    def encrypt_password(self, password, salt=False):
        algo="sha1"
        lib = hashlib.__getattribute__(algo) 
        salt = salt if salt else lib(str(random.random())).hexdigest()[:5]
        hash = lib("%s%s"%(salt, password)).hexdigest()
        return "%s$%s$%s" % (algo, salt, hash)
        
    def check_password(self, password):
        try:
            print self.password
            algo, salt, hash = str(self.password).split("$")
            return self.password == self.encrypt_password(password, salt)
        except Exception as e: 
            self.logger.exception(e)
            return False
    
    def spoton_account_save(self, data=None):
        spoton_users_collection = self.__conn__['spoton']['users']
        spoton_user = spoton_users_collection.find_one({'username':data["username"]})
        lib = hashlib.__getattribute__("sha1") 
        hex = lib(data['password']).hexdigest()
        if spoton_user:
            spoton_users_collection.update({'username':data["username"]},{'$set':{'password':hex}})
        else:
            spoton_users_collection.insert({'username':data["username"],'password':hex,'hotspot_account':True})
    
    def save(self, session=None, data=None):
        res = False
        if data:
            self.spoton_account_save(data)
            if data.get("password", None) and data["password"].strip() != "":
                if data['password'] == data['password_confirm']:
                    del data['password_confirm']
                    data['password'] = self.encrypt_password(data['password'])
                    res = super(User, self).save(session, data)
                else: 
                    res = False
                    self.__errors__["password"] = "Passwords don't match"
            else:
                del data['password']
                del data['password_confirm']
                res = super(User, self).save(session, data)
        else:
            res = super(User, self).save(session, data)
            
        return res
  
