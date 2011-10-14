import re, inspect
from pymongo.objectid import ObjectId
import datetime
from widget import *
import settings
import util

EMPTY_VALUES = ["", u"", None, " "]

increment = util.sequence

class Field(object):
    __name__ = None
    __widget__ = None
    __old__ = None
    __value__  = None
    __required__ = False
    __default__ = None
    __id__ = None
    __errormessage__ = None
    __label__ = None
    __error__ = None
    __disabled__ = False
    __parent__ = None
    __args__ = ()
    __kwargs__ = {}
    __namespace__ = None
    __inited__ = False
    
    
    def __init__(self, *args, **kwargs):
        self.__inited__ = False
        self.__value__ = None
        self.__name__ = kwargs.get('name', None)
        self.__widget__ = kwargs.get('widget', TextInput)
        self.__required__ = kwargs.get('required', False)
        self.__default__ = kwargs.get('default', None)
        self.__label__ = kwargs.get('label', None)
        self.__id__ = kwargs.get('id', None)
        self.__disabled__ = kwargs.get('disabled', None)
        self.__errormessage__ = kwargs.get('error', None)
        self.__namespace__ = None
        self.__error__ = None
        self.__args__ = args
        self.__kwargs__ = kwargs

    def __getvalue__(self):
        return self.__value__
    
    def __setvalue__(self, value):
        try:
            if value == None and self.__default__ != None and self.__inited__: value = self.__default__
            value = self.__clean__(value)
            try:
                if self.__widget__: value = self.__widget__(field=self).__clean__(value)
            except Exception as e:
                raise e
            self.__old__ = self.__value__
            self.__value__ = value
            self.__inited__ = True
        except Exception as e:
            self.__error__ = e
            self.__value__ = None
            self.__inited__ = True
            raise e        
        
    def __delete__(self, instance):
        self.__value__ = None
    
    def __clean__(self, value):
        if value in EMPTY_VALUES:
            if self.__required__:
                ex = Exception("Required Field")
                self.__error__ = ex
                raise ex
            else:
                value = None        

        return value
    
    @property
    def name(self):
        return self.__name__
    
    @property
    def label(self):
        return self.__label__
        
    @property
    def hidden(self):
        return True if self.__widget__.__type__ == 'hidden' else False
    
    @property
    def val(self):
        if self.__value__ == None and self.__default__ != None: return self.__default__
        return self.__value__
    
    @property
    def old(self):
        return self.__old__
        
    @property
    def req(self):
        return self.__required__
        
    @property
    def namespace(self):
        return self.__namespace__
    
    
    def render(self, **kwargs): 
        if self.__disabled__:kwargs['disabled'] = "DISABLED"
        if kwargs.get("cls", None):
            kwargs['class'] = kwargs.get("cls")
            del kwargs['cls']
        return self.__widget__(self, **kwargs).render(**kwargs)
            
    
        
class Char(Field):
    __min__ = None
    __max__ = None
    
    def __init__(self, min=None, max=None, *args, **kwargs):
        self.__min__ = min
        self.__max = max
        super(Char, self).__init__(*args, **kwargs)    
            
    
    def __clean__(self, value):
        ex = None
        try:
            value = super(Char, self).__clean__(value)
            if value: value = unicode(value)
            if self.__min__ and (len(value) < self.__min__): ex = Exception("Value length must be longer than " % self.__min__)
            if self.__max__ and (len(value) > self.__max__): ex = Exception("Value length must be shorter than " % self.__max__)
            if ex:
                self.__error__ = ex
                raise ex
            return value
        except Exception as e:
            self.__error__ = e
            raise e
            
class Password(Field):
    
    def __setvalue__(self, value):
        if value not in EMPTY_VALUES: super(Password, self).__setvalue__(value)
            
class Integer(Field):
    __min__ = None
    __max__ = None
    
    def __init__(self, min=None, max=None, *args, **kwargs):
        self.__min__ = min
        self.__max__ = max
        super(Integer, self).__init__(*args, **kwargs)
    
    def __clean__(self, value):        
        ex = None
        try:
            value = super(Integer, self).__clean__(value)
            if value: value = int(value)
            if self.__min__ and (value < self.__min__): ex = Exception("Value must be greater than " % self.__min__)
            if self.__max__ and (value > self.__max__): ex = Exception("Value must be less than " % self.__max__)
            if ex:
                self.__error__ = ex
                raise ex
            return value
        except Exception as e:
            raise Exception("Not an integer")

class Float(Field):
    __min__ = False
    __max__ = False
    
    
    def __clean__(self, value):
        ex = None
        try:
            value = super(Float, self).__clean__(value)
            if value: value = float(value)
            if self.__min__ and (value < self.__min__): ex = Exception("Value must be greater than " % self.__min__)
            if self.__max__ and (value > self.__max__): ex = Exception("Value must be less than " % self.__max__)
            if ex:
                self.__error__ = ex
                raise ex
            return value
        except Exception as e:
            raise Exception("Not a float")

class Choice(Field):
    __choices__ = []
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', Select)
        self.__choices__ = kwargs.get('choices', [])
        super(Choice, self).__init__(*args, **kwargs)
    
    @property
    def choices(self):
        return self.__choices__
        
    def __clean__(self, value):
        ex = None
        try:
            value = super(Choice, self).__clean__(value)
            vals = [opt['value'] if isinstance(opt, dict) else opt for opt in self.__choices__]
            if value and not value in vals:
                ex = Exception("Value given is not a valid option")
                self.__error__ = ex
                raise ex
            return value
        except Exception as e:
            raise e

def choice_display(choice): 
    return text
    
class CollectionChoice(Choice):
    
    def __clean__(self, value): 
        try:
            return int(value)
        except:
            return value
    
    def render(self, **kwargs):
        db = self.__kwargs__['db']
        collection = self.__kwargs__['collection']
        query = self.__kwargs__.get('query', {})
        fields = self.__kwargs__.get('fields', {'_id':1})
        sort = self.__kwargs__.get('sort', [('_id',1)])
        skip = self.__kwargs__.get('skip', 0)
        limit = self.__kwargs__.get('limit', 2000)
        display = self.__kwargs__.get('display', choice_display)
        value = self.__kwargs__.get('value', '_id')
        self.__choices__ = [display(choice) for choice in settings.CONNECTION[db][collection].find(query, fields=fields, sort=sort, skip=skip, limit=limit)]
        return super(CollectionChoice, self).render(**kwargs)
        
    
class Boolean(Field):
    __default__ = False
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', CheckBox)
        super(Boolean, self).__init__(*args, **kwargs)
    
    def __clean__(self, value):
        ex = None
        try:
            value = super(Boolean, self).__clean__(value)
            return bool(value)
        except Exception as e:
            self.__error__ = e
            raise Exception("Not a boolean")

class Regex(Char):
    __reg__ = None
    
    def __init__(self, regex, *args, **kwargs):
        super(Regex, self).__init__(*args, **kwargs)
        if isinstance(regex, basestring): regex = re.compile(regex)
        self.__reg__ = regex

    def __clean__(self, value):
        ex = None
        try:            
            value = super(Regex, self).__clean__(value)
            if value: 
                if not self.__reg__.search(value): raise Exception(self.__errormessage__)
        except Exception as e:
            raise e
        return value

class Email(Regex):
    email_re = re.compile(
    r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
    r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
    r')@(?:[A-Z0-9-]+\.)+[A-Z]{2,6}$', re.IGNORECASE)  # domain
    
    def __init__(self, *args, **kwargs):
        kwargs['error'] = u'Enter a valid e-mail address.'
        super(Email, self).__init__(regex=self.email_re, *args, **kwargs)
        
        
class MongoId(Field):
    __clstype__ = None
    __obj__ = None
    
    def __init__(self, *args, **kwargs):
        super(MongoId, self).__init__(*args, **kwargs)
        self.__clstype__ = kwargs.get('type', None)
    
    def __call__(self):
        if self.__value__:
            self.__obj__ = self.__clstype__(id=self.__value__) if not self.__obj__ else self.__obj__
            return self.__obj__
        else: return None
    
    def __clean__(self, value):
        ex = None
        try:
            value = super(MongoId, self).__clean__(value)
            if value: value = ObjectId(value)
        except: pass
        if (self.__required__ == False and value in EMPTY_VALUES) or isinstance(value, ObjectId): return value
        else: 
            ex = Exception(u'The value given is not a valid ObjectID')
            self.__error__ = ex
            raise ex
        return value

def model_display(choice):
    return {'value':choice.__id__, 'display':choice.name}
    

class ModelChoice(MongoId):
    
    __choices__ = []
    
    def __init__(self, *args, **kwargs):
        kwargs['widget'] = kwargs.get('widget', Select)
        super(ModelChoice, self).__init__(*args, **kwargs)
    
    @property
    def choices(self):
        return self.__choices__
    
    def render(self, **kwargs):
        type = self.__kwargs__['type']
        query = self.__kwargs__.get('query', {})
        sort = self.__kwargs__.get('sort', [('_id',1)])
        display = self.__kwargs__.get('display', model_display)
        value = self.__kwargs__.get('value', '_id')
        self.__choices__ = [display(choice) for choice in type.find(query)]
        if self.__kwargs__.has_key('prepend'):
            self.__kwargs__['prepend'].extend(self.__choices__)
            self.__choices__ = self.__kwargs__['prepend']
        if self.__kwargs__.has_key('append'):
            self.__choices__.extend(self.__kwargs__['append'])
        return super(ModelChoice, self).render(**kwargs)


class Date(Field):
    
    def __clean__(self, value):
        ex = None
        try:
            value = super(Date, self).__clean__(value)
        except Exception as e: raise e
        if isinstance(value, datetime.datetime): return value
        else:
            if value in EMPTY_VALUES and self.__required__:
                ex = Exception(u'The value given is not a valid datetime object')
                self.__error__ = ex
                raise ex
            else:
                return value

class TimeStamp(Date):
    
    def __setvalue__(self, value):
        if self.__inited__ and not value:
            value = datetime.datetime.utcnow()
        super(TimeStamp, self).__setvalue__(value)

class AutoIncrement(Integer):
    
    def __setvalue__(self, value):
        if value not in EMPTY_VALUES and value != 'increment':
            super(AutoIncrement, self).__setvalue__(value)
        elif self.__inited__ or value == 'increment':
            self.__value__ = util.sequence(field=self.__name__)
        self.__inited__ = True
