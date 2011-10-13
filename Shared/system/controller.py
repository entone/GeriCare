import os, time, re, locale
import settings
from system.singleconnection import SingleConnection
from system.jsonobject import JSONObject
import system.util as util
from pymongo.errors import *
from pymongo.objectid import ObjectId

from system.jsonobject import JSONObject
from system.decorators import permissions
from libraries.DateFormatter import DateFormatter
import system.helpers as helpers
        

locale.setlocale(locale.LC_ALL, '')

class Controller(object):
    _conn = None
    db = None
    views = None
    session = None
    server = None
    
    #this will override the permissions decorators
    class Permissions(object):pass
    
    class Meta:
        db = 'spoton'
        collection = 'merchants'
        field = ''
        table_template = ''
        template = ''
        cls = None
        view = None
        form = None
        new_form = None
    
    def check_permissions(self, method):
        if hasattr(self.Permissions, method): 
            return self.Permissions.__dict__[method].allowed(cls=self)
        else:
            return True
    
    def __init__(self, session=None, server=None):
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        self.session = session
        self.server = server
        self.connect()
        self.db = self._conn[self.Meta.db]        
        self.admin_db = self._conn[settings.ADMIN_DB]
        self.collection = self._conn[self.Meta.db][self.Meta.collection]
    
    
    
    def connect(self):     
        while not self._conn:
            try:
                self._conn = SingleConnection(settings.MONGO_HOSTS)
            except AutoReconnect, e: 
                self.logger.error(e)
                time.sleep(1)
                
    def render(self, uri, args={}):
        try:
            template = settings.VIEWS.get_template(uri)
            args['session'] = self.session
            args['DateFormatter'] = util.format_date
            args['controller'] = self.__class__.__name__
            args['base_url'] = settings.BASE_URL
            args['static_url'] = helpers.static_url
            args['absolute_url'] = helpers.absolute_url
            args['linkify'] = util.linkify
            args['locale'] = locale
            args['settings'] = settings
            return template.render(**args)
        except Exception as e:
            self.logger.exception(e)
            pass
    
    def remove_element(self, element=""):
        attributes = ["id", "attribute", "position", "new"]        
        result = {}
        self.logger.debug(element)
        vars = element.split(':_:')[1:]
        count = 0
        for key in attributes:
            try: result[key] = vars[count]
            except: 
                result[key] = None
            count+=1
        
        self.logger.debug(result)
        id = ObjectId(result['id']) if (result['id'] and result['id'] != 'None') else None
        object = self.Meta.cls(id=id)
        return JSONObject(success=object.remove_element(result))
    
    def compile_query(self, query=None):
        qu = {}
        if query:
            q = re.compile('%s' % query, re.IGNORECASE)
            qu['$or'] = []
            for i in self.Meta.fields:
                ind = i.find(":")
                if -1 != ind:                    
                    if i[0:ind] == 'int':
                        try: 
                            int(query)
                            qu['$or'].append({i[(ind+1):]:int(query)})
                        except: pass
                else:
                    qu['$or'].append({i:q})
            self.logger.debug(qu)
        return qu
    
    def search(self, query=None):
        self.Meta.cls.__currentview__ = self.Meta.view
        qu = self.compile_query(query)        
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find(qu).sort("_id", -1), 'columns':columns}
        return JSONObject(success=True, html=self.render(self.Meta.table_template, args))
    
    def save(self, **kwargs):
        for id, data in kwargs['form'].iteritems():
            if id != 'None': obj = self.Meta.cls(id=id)
            else: obj = self.Meta.cls()
            if obj.save(self.session, data):
                ret = JSONObject(success=True, data={'id':str(obj.__id__)})
            else:
                obj.__errors__['__id__'] = str(obj.__id__)
                ret = JSONObject(success=False, data=obj.__errors__, action='error')
            
            return ret
        
    def get_all(self):
        self.Meta.cls.__currentview__ = self.Meta.view
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find().sort("_id", -1), 'columns':columns}
        return JSONObject(success=True, html=self.render(self.Meta.table_template, args), action='replace')
    
    def index(self): return self.show_all()
    
    #@permissions(level=9)
    def show_all(self):
        self.Meta.cls.__currentview__ = self.Meta.view
        columns = self.Meta.cls().__view__.columns
        args = {'objects':self.Meta.cls.find().sort("_id", -1), 'columns':columns}
        return self.render(self.Meta.template, args)
        
                        
    def get_one(self, id=None):
        self.Meta.cls.__currentview__ = None
        object = self.Meta.cls(id=ObjectId(id), view=self.Meta.form)
        return JSONObject(html=object.render(), action='replace')
        
    def get_new(self):
        self.Meta.cls.__currentview__ = None
        object = self.Meta.cls(view=self.Meta.new_form)
        return object.render()
