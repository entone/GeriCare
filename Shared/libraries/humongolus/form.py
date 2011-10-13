import field
import relationship
import document

class Form(object):
    __context__ = None
    __action__='save'
    __tag__=None
    
    def __init__(self, context):
        super(Form, self).__init__()
        self.__context__ = context
    
    def render(self, attrs=None, id=None):
        tag = self.__tag__
        action = self.__action__
        parts = []
        
        id = "id='%s'" % id if id else ""
        
        cls = 'class="open"' if not self.__context__.__parent__ else ''
        if tag:
            part = u"<%s data-id='%s' %s>" % (tag, self.__context__.__namespace__, cls) if self.__context__.__namespace__ else u"<%s data-id='%s-%s' %s>" % (tag, self.__context__.__class__.__name__, str(self.__context__.__id__), cls)
        else:
            part = u"<div class='fieldset' data-id='%s' %s>" % (self.__context__.__namespace__, cls) if self.__context__.__namespace__ else u"<form action='%s' %s><div class='fieldset' data-id='%s.%s'>" % (action, id, self.__context__.__class__.__name__, str(self.__context__.__id__))
            
        parts.append(part)
        if not self.__context__.__namespace__: 
            if not self.__context__.__id__:
                st = 'New'
            else:
                st = self.__context__.__id__
                
            part = u"<div class='legend'>%s</div>" % st
        else:
            part = u"<div class='legend'>%s</div>" % self.__context__.__class__.__name__
            
        parts.append(part)
        for k in self.__context__.__fieldorder__:
            at_k = self.__context__.__dict__.get(k, None)
            if isinstance(at_k, field.Field):
                try:
                    cls = 'required' if at_k.__required__ else ''
                    part = u"<label for='id_%s' class='%s'>%s</label>" % (at_k.name, cls, at_k.label) if at_k.label and not at_k.hidden else ""
                    if at_k.__widget__.__type__ == 'checkbox':
                        parts.append(at_k.render())
                        parts.append(part)
                    else:                            
                        parts.append(part)
                        parts.append(at_k.render())
                    
                except Exception as e:
                    self.__context__.logger.exception(e)
            elif isinstance(at_k, (document.base, relationship.Relationship)):
                parts.append(u"".join(at_k.__render__()))
        
        if tag:
            part = u"</%s>" % tag
        else:
            part = u"</div>" if self.__context__.__namespace__ else u"</div></form>"
        parts.append(part)        
        return parts