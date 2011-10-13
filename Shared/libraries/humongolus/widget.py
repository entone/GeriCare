import util
import settings
import datetime
import field

EMPTY_VALUES = ["", u"", None, " "]

class Widget(object):
    __args__ = {}
    __tag__ = "input"
    __type__ = "text"
    __field__ = None
    
    def __init__(self, field, *args, **kwargs):
        self.__field__ = field        
        self.__args__ = kwargs
        
        
    def att_string(self, args=None):
        args = args if args else self.__args__
        
        atts = []
        for k,v in args.iteritems():
            v = v if isinstance(v, list) else [v]
            atts.append(u"%s='%s'" % (k, u" ".join([util.escape(val) for val in v])))
        
        return u" ".join(atts)
    
    def __clean__(self, value): return value
    
    def render(self, **kwargs):
        kwargs['type'] = kwargs['type'] if kwargs.get('type') else self.__type__
        if not kwargs.has_key('value'):
            kwargs['value'] = self.__field__.val if self.__field__.val != None else ""
        kwargs['name'] = kwargs['name'] if kwargs.get('name') else self.__field__.name
        if self.__field__.__required__: 
            kwargs['class'] = kwargs['class'] if kwargs.get('class', None) else []
            kwargs['class'].append('required')
        if not kwargs.get('id', None): kwargs['id'] = "id_%s" % self.__field__.name
        self.__args__.update(kwargs)
        return u"<%s %s/>" % (self.__tag__, self.att_string())


class TextInput(Widget): pass
        
class Password(Widget):
    __type__ = "password"
    
    def render(self, **kwargs):
        kwargs['value'] = ""
        return super(Password, self).render(**kwargs)
        
class ConfirmPassword(Widget):
    __type__ = "password"
    
    def render(self, **kwargs):
        kwargs['value'] = ""
        st = super(ConfirmPassword, self).render(**kwargs)
        st = st + "<label>Confirm Password</label>"
        kwargs['name'] = self.__field__.name+"_confirm"
        st = st+ super(ConfirmPassword, self).render(**kwargs)
        return st
        
        
class TextArea(Widget):
    __tag__ = "textarea"
    
    def render(self, **kwargs):
        kwargs['name'] = self.__field__.name
        self.__args__.update(kwargs)
        val = self.__field__.val if self.__field__.val != None else ""
        return u"<%s %s>%s</%s>" % (self.__tag__, self.att_string(), val, self.__tag__)
        
class CheckBox(Widget):
    __type__ = "checkbox"
    
    def render(self, **kwargs):
        if self.__field__.val is True: kwargs['checked'] = 'CHECKED'
        if not kwargs.has_key('value'): kwargs['value'] = "1"
        return super(CheckBox, self).render(**kwargs)
        

class Select(Widget):
    
    def render(self, **kwargs):
        if hasattr(self.__field__, 'choices'): return self.build(**kwargs)
        raise Exception("Incompatiable Field for Select Widget")
        
    def build(self, **kwargs):
        kwargs['name'] = self.__field__.name
        options = []
        for opt in self.__field__.choices:
            opt_args = {}
            if isinstance(opt, dict): 
                value = opt['value']
                display = opt['display']
            else: 
                value = opt
                display = opt
            opt_args['value'] = value
            if value == self.__field__.val: opt_args['selected'] = 'selected'
            options.append(u"<option %s>%s</option>" % (self.att_string(args=opt_args), util.escape(display)))
        
        self.__args__.update(kwargs)
        return u"<select %s>%s</select>" % (self.att_string(), u"".join(options))
        
        
class Hidden(Widget):
    __type__ = "hidden"   

class Date(Widget):
    
    def __clean__(self, value):
        try:
            if isinstance(value, datetime.datetime): return value
            #print "PARSING DATE:: %s" % value
            if not value in EMPTY_VALUES:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            else:
                return None
        except Exception as e:
            raise e
    
    def render(self, **kwargs):
        if self.__field__.__value__ and not kwargs.get('value', None): kwargs['value'] = datetime.datetime.strftime(self.__field__.__value__, "%Y-%m-%d %H:%M:%S.%f")
        return super(Date, self).render(**kwargs)

class TimeStamp(Widget):
    def render(self, **kwargs):
        kwargs['value'] = self.__field__.__value__ if self.__field__.__value__ else datetime.datetime.utcnow()
        return super(TimeStamp, self).render(**kwargs)

    def __clean__(self, value):
        try:
            if isinstance(value, datetime.datetime): return value
            if not value in EMPTY_VALUES:
                return datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S.%f")
            else:
                return None
        except Exception as e:
            raise e


class Link(Widget):
    def render(self, **kwargs):
        return "<a href='%s' target='_blank'>Facebook Account</a>" % self.__field__.__value__
        

class ObjectView(Widget):
    def render(self, **kwargs):
        kwargs['type'] = 'hidden'
        st = super(ObjectView, self).render(**kwargs)
        if isinstance(self.__field__, field.MongoId): return st+self.__field__().view()
        else: return st + "<p>%s</p>" % self.__field__.__value__
