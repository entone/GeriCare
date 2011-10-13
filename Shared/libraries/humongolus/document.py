import settings
import copy
import util
import field
import relationship
import form


from pymongo.objectid import ObjectId
import pymongo

class base(object):
    __namespace__  = None
    __document__ = {}
    __errors__ = {}
    __values__ = {}
    __data__ = {}
    __update__ = {}
    __query__ = {}
    __fieldorder__ = ()
    __inited__ = False
    __args__ = ()
    __kwargs__ = {}
    __parent__ = None
    logger = None
    __indexed__ = False
    
    def __new__(cls, *args, **kwargs):
        cls.__values__ = {}
        for b in cls.__getbases__():
            for n,f in b.__dict__.iteritems():
                if isinstance(f, (base, relationship.Relationship, field.Field)):               
                    inst = f.__class__(*f.__args__, **f.__kwargs__)                 
                    if isinstance(f, field.Field): inst.__name__ = n
                    cls.__values__[n] = inst
        for k,v in cls.__dict__.iteritems():
            if isinstance(v, (base, relationship.Relationship, field.Field)):
                inst = v.__class__(*v.__args__, **v.__kwargs__)
                if isinstance(inst, field.Field): inst.__name__ = k
                cls.__values__[k] = inst
        
        cls.__ensureindexes__()
        return super(base, cls).__new__(cls)
    
    
    @classmethod
    def __ensureindexes__(cls):
        if not cls.__indexed__ and cls.__dict__.get('__dbindexes__'):
            for i in cls.__dict__.get('__dbindexes__'):
                print i.kwargs()
                settings.CONNECTION[cls.__db__][cls.__collection__].ensure_index(**i.kwargs())
            
            cls.__indexed__ = True
    
    @classmethod
    def __getbases__(cls):
        b = []        
        for i in cls.__bases__:
            b.append(i)
            try:
                b.extend(i.__getbases__())
            except:pass
        
        return b
        
    
    def __init__(self, *args, **kwargs):
        self.__document__ = {}
        self.__get_logger__()
        self.__args__ = args
        self.__kwargs__ = kwargs
        self.__errors__ = {}
        self.__inited__ = False
        self.__form__ = kwargs.get('form', form.Form)
        try: del kwargs['form']
        except: pass
        for k,v in self.__values__.iteritems(): self.__dict__[k] = v
        
        
    def __json__(self):
        obj = {}
        for k,v in self.__dict__.iteritems():
            if isinstance(v, (base, field.Field, relationship.Relationship)):
                if isinstance(v, field.Field):
                    obj[k] = v.val
                elif isinstance(v, (base, relationship.Relationship)):
                    obj[k] = v.__json__()
        
        return obj
   
    def __get_logger__(self):
        self.logger = settings.LOGGER(settings.LOG, self.__class__.__name__)
    
    
    def __map__(self, doc, nsp=None):
        self.__errors__ = {}
        self.__namespace__ = nsp
        self.__inited__ = True
        self.__document__ = doc
        for k,v in self.__dict__.iteritems():
            if isinstance(v, (base, field.Field, relationship.Relationship)):
                v.__parent__ = ObjectId(self.__id__) if self.__id__ else ObjectId(self.__parent__)
                ns = "%s.%s" % (self.__namespace__, k) if self.__namespace__ else k
                if isinstance(v, field.Field):
                    value = None
                    try: 
                        value = doc.get(k, None)
                        #see if we already have it
                        if value == None:
                            try: value = v.__value__
                            except: pass
                    except Exception as e: self.logger.exception(e)
                    v.__namespace__ = ns
                    setattr(self, k, value)
                elif isinstance(v, (base, relationship.Relationship)):                    
                    if isinstance(v, base):
                        value = doc.get(k, {})
                    elif isinstance(v, relationship.Relationship):
                        value = doc.get(k, v.__rep__)
                    v.__map__(value, ns)
    
    def __setattr__(self, name, value):
        if self.__dict__.has_key(name):
            var = self.__dict__[name]
            if isinstance(var, field.Field):
                try:
                    try:
                        var.__error__ = None
                        del self.__errors__[var.__namespace__]
                    except: pass
                    var.__setvalue__(value)
                except Exception as e:
                    #self.logger.exception(e)
                    self.__errors__[var.__namespace__] = e
                    pass
            else:
                self.__dict__[name] = value
        else:
            self.__dict__[name] = value
            
    
    def __getattribute__(self, name):
        try:
            var = object.__getattribute__(self, name)                        
        except AttributeError:
            return None
            #raise AttributeError
        
        if isinstance(var, field.Field): return var.__getvalue__()
        return var
    
    def field(self, name):
        try:
            var = object.__getattribute__(self, name)                        
            return var
        except AttributeError:
            return None
    
    def __save__(self, new=False):
        self.__update__ = {}
        self.__update__['$set'] = {}
        self.__update__['old'] = {}
        self.__update__['$addToSet'] = {}
        for k,v in self.__dict__.iteritems():
            if isinstance(v, (base, field.Field, relationship.Relationship)):
                ns = "%s.%s" % (self.__namespace__, k) if self.__namespace__ else k                
                if isinstance(v, field.Field):
                    if not v.__error__:     
                        if v.old != v.val or not self.__inited__:
                            self.__update__['$set'][ns] = v.val
                            self.__update__['old'][ns] = v.old
                    else:
                        self.__errors__[v.__namespace__] = v.__error__
                elif isinstance(v, (base, relationship.Relationship)):                    
                    try:
                        res = v.__save__(new)
                        for k,v in res['$addToSet'].iteritems():
                            self.__update__['$addToSet'][k] = v
                        self.__update__['$set'].update(res['$set'])
                        self.__update__['old'].update(res['old'])
                    except Exception as e:
                        self.logger.debug("ERRORS")
                        self.logger.exception(e)
                        self.__errors__.update(v.__errors__)
        
        if len(self.__errors__.keys()):
            self.logger.debug(self.__errors__) 
            raise Exception("Error")
        return self.__update__
    
    def __render__(self, form=None, action=None, attrs=None, id=None):
        if not self.__form__ and not form: raise Exception("No Form")
        cls = form if form else self.__form__
        fo = cls(context=self)
        if action: fo.__action__ = action
        return fo.render(attrs=attrs, id=id)

class Document(base):
    __db__ = None    
    __collection__ = None
    __id__ = None
    __conn__ = None
    __dbindexes__ = []
    
    collection = None
    
    def __init__(self, *args, **kwargs):
        self.__id__ = kwargs.get('id', None)
        super(Document, self).__init__(*args, **kwargs)        
        self.__conn__ = settings.CONNECTION
        if self.__conn__ and self.__collection__: self.collection = self.__conn__[self.__db__][self.__collection__]
        if self.__id__: 
            self.handle_id(self.__id__)
        else: self.__map__({}, self.__namespace__)
        
    def handle_id(self, id):
        self.__id__ = id            
        if self.__id__:
            self.__id__ = ObjectId(self.__id__)
            self.__get_document__()                
        else:
            self.logger.debug("No connection or collection defined")        
        
        self.__map__(self.__document__, self.__namespace__)
        
    def __presave__(self, new=False):pass
    
    def __postsave__(self, new=False):pass
    
    def save(self):
        errors = False if len(self.__errors__.keys()) == 0 else True
        self.__isnew__ = False
        if self.__id__:
            try:
                self.__presave__()
                self.__save__()
                self.__postsave__()
            except Exception as e:
                self.__errors__.update({'Error':e.message})
                self.logger.exception(e)
                raise e
            if len(self.__update__.keys()): 
                try:
                    obj = {}
                    for k,v in self.__update__.iteritems():
                        if k != 'old': obj[k] = v
                    
                    query = {'_id':self.__id__}
                    res = self.collection.update(query, obj)
                    return True
                except Exception as e:
                    raise e
        else:
            try:
                self.__isnew__ = True
                self.__presave__(new=True)
                self.__save__(new=True)
                self.__postsave__(new=True)
                res = self.collection.insert(self.__json__())
                self.__id__ = res            
                self.__update__['$set']['new'] = res
                self.__update__['old'] = {"new":None}
                return True
            except Exception as e:
                raise e
        raise Exception("Errors")
    
    def __str__(self):
        if self.name: return self.name
        else: return self.__class__.__name__
    
    def view(self):
        return str(self)
    
    def __iter__(self):
        return self
    
    def __setitem__(self, key, value):
        if key == '_id': 
            self.__id__ = value
            self.__get_document__()
            self.__map__(self.__document__, self.__namespace__)
        pass
    
    @classmethod
    def find(cls, query={}):
        keys = {'_id':1}
        cur = settings.CONNECTION[cls.__db__][cls.__collection__].find(query, keys, as_class=cls)
        return cur
    
    @classmethod
    def find_one(cls, query={}):
        keys = {'_id':1}
        obj = settings.CONNECTION[cls.__db__][cls.__collection__].find_one(query, keys, as_class=cls)
        return obj
        
    def __get_document__(self):
        self.__document__ = self.collection.find_one({'_id':self.__id__})
        if not self.__document__: self.__document__ = {}
                

class EmbeddedDocument(base):
    
    def __init__(self, *args, **kwargs):
        super(EmbeddedDocument, self).__init__(*args, **kwargs)
        self.__map__({}, self.__namespace__)
        
class Index(object):
    field = ""
    sort = pymongo.ASCENDING
    name = ""
    unique = False
    drop_dups = False
    background = True
    ttl = 9999999
    min = 0
    max = 0
    
    ASECENDING = pymongo.ASCENDING
    DESCENDING = pymongo.DESCENDING
    GEO2D = pymongo.GEO2D
    
    def __init__(self, **kwargs):
        if not kwargs.get('field', None): raise Exception("Field name is required")
        for k,v in kwargs.iteritems():
            if getattr(self, k) != None:
                setattr(self, k, v)
    
    
    def kwargs(self):
        return {"key_or_list":[(self.field, self.sort)], "deprecated_unique":False, "ttl":self.ttl, "name":self.name, "unique":self.unique, "drop_dups":self.drop_dups, "background":self.background, "min":self.min, "max":self.max}
    
    
    
