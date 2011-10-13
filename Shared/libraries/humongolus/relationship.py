import settings
import time, random

class Relationship(object):
    __namespace__ = None
    __update__ = {}
    __inited__ = False
    __type__ = None
    __errors__ = {}
    __rep__ = {}
    __args__ = ()
    __kwargs__ = {}
    __parent__ = None
    __haschild__ = False
        
    
    def create(self, type=None, view=None):
        try:
            obj = self.__type__()
            obj.__map__({}, "%s.%s" % (self.__namespace__, "%s%s" % (time.time(), random.randint(1000, 1000000))))
            return obj
        except Exception as e:
            raise e
    
    
    def __map__(self, doc, ns):pass
    def __json__(self):pass
    def __render__(self):pass
    
    def __save__(self, new=False):
        self.__errors__ = {}
        self.__update__ = {}
        self.__update__['$set'] = {}
        self.__update__['$addToSet'] = {}
        self.__update__['old'] = {}
        if not self.__haschild__ and len(self) > 0:
            self.__update__['$addToSet'][self.__namespace__] = {}
            for obj in self:
                try:
                    res = obj.__save__(new)                    
                except Exception as e:
                    self.__errors__.update(obj.__errors__)
            self.__update__['$addToSet'][self.__namespace__]['$each'] = [obj.__json__() for obj in self]
        else:
            for obj in self:
                try: 
                    res = obj.__save__(new)
                    print res
                    self.__update__['$addToSet'].update(res['$addToSet'])
                    self.__update__['$set'].update(res['$set'])
                    self.__update__['old'].update(res['old'])
                except Exception as e:
                    self.__errors__.update(obj.__errors__)

        if len(self.__errors__.keys()): raise Exception("Errors")
        return self.__update__

class Dict(dict, Relationship):
    
    def __init__(self, type=None, *args):
        super(Dict, self).__init__(*args)
        self.__errors__ = {}
        self.__args__ = args
        self.__kwargs__ = {'type':type}
        self.__type__ = type
    
    def __save__(self, new=False):
        self.__update__['$set'] = {}
        self.__update__['old'] = {}
        self.__update__['$addToSet'] = {}
        for k,obj in self.iteritems():
            try: 
                res = obj.__save__(new)
                self.__update__['$set'].update(res['$set'])
                self.__update__['old'].update(res['old'])
            except Exception as e: self.__errors__.update(obj.__errors__)

        if len(self.__errors__.keys()): raise Exception("Errors")
        return self.__update__
    
    def __json__(self):
        ob = {}
        for k,obj in self.iteritems(): ob[k] = obj.__json__()
        return ob
        
    def __map__(self, doc, ns):
        self.__namespace__ = ns
        self.__inited__ = True
        for id,v in doc.iteritems():
            obj = self.get(id, None)
            if obj:
                obj.__parent__ = self.__parent__
                obj.__map__(v, "%s.%s" % (self.__namespace__, id))                
            else: 
                obj = self.__add_doc__(id, v)
                if obj: obj.__parent__ = self.__parent__
            
    def __add_doc__(self, key, doc):
        obj = self.__type__()
        obj.__map__(doc, self.__namespace__)
        self[key] = obj
        return obj
    
    def __setitem__(self, key, value):
        ns = "%s.%s" % (self.__namespace__, key)
        value.__namespace__ = ns
        super(Dict, self).__setitem__(key, value)
        
    def __render__(self):
        parts = []
        part = "<div class='fieldset' data-id='%s'>" % self.__namespace__
        parts.append(part)
        title = self.__namespace__.split(".")[-1].capitalize()
        part = "<div class='legend'>%s</div>" % title
        parts.append(part)
        for k,obj in self.iteritems():
            parts.append(u"".join(obj.__render__()))
        
        part = "</div>"
        parts.append(part)
        return parts
            

class List(list, Relationship):
    __rep__ = []
    __haschild__ = False
    
    def create(self, type=None, view=None):
        try:
            obj = self.__type__()
            obj.__map__({}, "%s.%s" % (self.__namespace__, "%s|%s" % (time.time(), random.randint(1000, 1000000))))
            return obj
        except Exception as e:
            raise e
    
    def __init__(self, type=None, *args):
        super(List, self).__init__(*args)
        self.__errors__ = {}
        self.__args__ = args
        self.__kwargs__ = {'type':type}
        self.__type__ = type
    
    
    def __json__(self):
        li = []
        for obj in self: li.append(obj.__json__())
        return li
    
    def __map__(self, doc, ns=None):
        self.__namespace__ = ns
        self.__inited__ = True
        update = False
        if isinstance(doc, list):
            iter = enumerate(doc) 
        elif isinstance(doc, dict):
            update = True
            iter = doc.iteritems()
        for id,dic in iter:            
            try:
                obj = self[int(id)]
                obj.__parent__ = self.__parent__
                obj.__map__(dic, "%s.%s" % (self.__namespace__, id))
                if not update: self.append(obj)
                self.__haschild__ = True
            except Exception as e:           
                obj = self.__add_doc__(dic)
            
    def __add_doc__(self, doc):
        obj = self.__type__()        
        ns = "%s.%s" % (self.__namespace__, len(self))
        obj.__parent__ = self.__parent__
        obj.__map__(doc, ns)
        self.append(obj)
        self.__haschild__ = True
        return obj
    
    def __setitem__(self, key, value):
        ns = "%s.%s" % (self.__namespace__, key)
        value.__namespace__ = ns
        super(List, self).__setitem__(key, value)
    
    def append(self, obj):
        ns = "%s.%s" % (self.__namespace__, len(self))
        obj.__namespace__ = ns
        super(List, self).append(obj)    
        
        
    def __render__(self):
        parts = []
        part = "<div class='fieldset' data-id='%s'>" % self.__namespace__        
        parts.append(part)
        if self.__namespace__: title = self.__namespace__.split(".")[-1].capitalize()
        else: title = ""
        part = "<div class='legend'>%s</div>" % title
        parts.append(part)
        for obj in self:
            parts.append(u"".join(obj.__render__()))
        part = "</div>"
        parts.append(part)
        return parts
        

class EmptyCursor(list):
    def count(self, *args, **kwargs): return len(self)
    def alive(self, *args, **kwargs): return False
    def distinct(self, *args, **kwargs): return self
    def limit(self, *args, **kwargs): return self
    def rewind(self, *args, **kwargs): pass
    def skip(self, *args, **kwargs): return self
    def sort(self, *args, **kwargs): return self
    def where(self, *args, **kwargs): pass

class Lazy(Relationship):
    __key__ = ""    
    __cursor__ = None
    def __init__(self, type=None, key=""):
        self.__haschild__ = False
        self.logger = settings.LOGGER(settings.LOG, self.__class__.__name__)
        self.__kwargs__ = {'type':type, 'key':key}
        self.__type__ = type
        self.__key__ = key
    
    def __call__(self, extra=None):
        if self.__parent__:
            self.logger.debug(self.__key__)
            self.logger.debug(self.__parent__)
            query = {self.__key__:self.__parent__}
            if extra: query.update(extra)
            self.__cursor__ = self.__type__.find(query) if not self.__cursor__ else self.__cursor__
            self.__cursor__.rewind()
            return self.__cursor__
        else: return EmptyCursor()
        
    
    def __save__(self, new=False):
        self.__update__ = {}
        self.__update__['$set'] = {}
        self.__update__['$addToSet'] = {}
        self.__update__['old'] = {}
        return self.__update__
