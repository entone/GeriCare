import libraries, locale
import humongolus.document as document
import datetime
import settings
from system.view import View
import system.util as util
import system.helpers as helpers
from system.singleconnection import SingleConnection

class Model(document.Document):
    __db__ = settings.DB
    __admindb__ = settings.ADMIN_DB
    __view__ = None    
    __currentview__ = None
    __logs__ = []
    
    def __init__(self, view=View, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        self.admin_db = self.__conn__[self.__admindb__]
        self.__logs__ = []                
        self.__view__ = view(context=self) if not self.__currentview__ else self.__currentview__(context=self)
        try:
            self.init(*args, **kwargs)
        except Exception as e:
            self.logger.exception(e)
            pass
        
    
    def save(self, session=None, data=None):
        if data:
            self.__map__(data)
        try:
            super(Model, self).save()
            self.log(session)
        except Exception as e:
            return False
            pass
        return True
    
    def init(self, *args, **kwargs): pass
    
    @classmethod
    def unique_field(cls, id, namespace, value, extra):
        conn = SingleConnection(settings.MONGO_HOSTS)
        parts = namespace.split(".")
        ns = []
        for i in parts:
            try: v = int(i)
            except: ns.append(i)
        
        ns_str = ".".join(ns)
        obj = {ns_str:value}
        if extra: obj.update(extra)
        res = conn[cls.__db__][cls.__collection__].find(obj, {'_id':1})
        for i in res:
            if i['_id'] == id: return True
        return False if res.count() > 0 else True
        
    
    def render(self, template=None, args={}):
        args['static_url'] = helpers.static_url
        args['absolute_url'] = helpers.absolute_url
        args['DateFormatter'] = util.format_date
        args['linkify'] = util.linkify
        args['locale'] = locale
        args['settings'] = settings
        return self.__view__.render(uri=template, args=args)
    
    def render_form(self, form=None, action=None, id=None):
        parts = self.__render__(form=form, action=action, id=id)
        parts.insert(-1, "<input type='submit' value='Submit' />")
        st = "\r\n".join(parts)
        return st
    
    def log(self, session=None):
        try:
            user = session.user if session else None
            for k,v in self.__update__['old'].iteritems():
                change = {
                    "old":v,
                    "reference":{"id":self.__id__, "collection":self.__collection__},
                    "when":datetime.datetime.utcnow(),
                    "value":self.__update__['$set'][k],
                    "field":k,
                    "user":user
                }
                #self.logger.debug(self.__admindb__)
                #self.logger.debug(self.__conn__)
                res = self.__conn__[self.__admindb__]['change_log'].insert(change)
        except Exception as e:
            self.logger.exception(e)
            pass


class EmbeddedModel(document.EmbeddedDocument):
    
    def __init__(self, view=View, *args, **kwargs):   
        super(EmbeddedModel, self).__init__(*args, **kwargs)
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        self.__logs__ = []
        self.__view__ = view(self)
        self.init(*args, **kwargs)
    
    def render(self, template=None, args={}):
        args['static_url'] = helpers.static_url
        args['absolute_url'] = helpers.absolute_url
        return self.__view__.render(uri=template, args=args)
    
    def init(self, *args, **kwargs):pass
