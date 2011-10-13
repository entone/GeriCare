import settings
import copy
from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import RichTraceback

class View(object):
    _template = 'models/default.html'
    def __init__(self, context):
        self._context = context
        
    def render(self, uri=None, args={}):
        uri = uri or self._template
        try:
            args['object'] = self._context
            template = settings.VIEWS.get_template(uri)
            return template.render_unicode(**args)
        except:
            traceback = RichTraceback()
            for (filename, lineno, function, line) in traceback.traceback:
                print "File %s, line %s, in %s" % (filename, lineno, function)
                print line, "\n"
            print "%s: %s" % (str(traceback.error.__class__.__name__), traceback.error)       
        
