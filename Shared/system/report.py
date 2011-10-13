from bson.code import Code
from gridfs import GridFS
from pymongo.objectid import ObjectId
import libraries, settings, csv, codecs, cStringIO
import humongolus.relationship as relationship
import humongolus.field as field
import humongolus.widget as widget
from csvhelpers import DictUnicodeWriter
from htmlhelpers import TableBuilder
import datetime, time

from system.model import Model, EmbeddedModel
from system.user import User
import system.util as util

from models.reports import get_available_reports as get_available_reports

class HtmlAttrs(EmbeddedModel):
    __fieldorder__ = ('kls', 'html_id')
    kls = field.Char(label='Class')
    html_id = field.Char(label='ID')
        
class Generator(Model):
    __fieldorder__ = ('output_format', 'data_start', 'data_end', 'status', 'notifications')
    __db__ = "hotspot"
    __collection__ = "report_occurences"
    
    parameters_template = "report_params/default.html"

    
    report = None #see below, circular class reference...
    requested = field.Date(label='Requested')
    started = field.Date(label='Started')
    completed = field.Date(label='Completed')
    status = field.Choice(label='Status', choices=['IDLE', 'IN_PROGRESS', 'COMPLETE', 'ERROR'], disabled=True)
    run_time = field.Float(label='Runtime')
    requested_by = field.MongoId(type=User, label='Requested By')
    notifications = relationship.List(type=User)
    data_start = field.Date(label='Start')
    data_end = field.Date(label='End')
    params = field.Field(label='Params')
    notes = field.Field(label='Notes')
    
    csv_output = field.MongoId(label='CSV Output')
    html_output = field.MongoId(label='HTML Output')
    result = field.Field(label='Result')
    map = field.Char(label='Map')
    reduce = field.Char(label='Reduce')
    finalize = field.Char(label='Finalize')
    
    def __init__(self, *args, **kwargs):
        super(Generator, self).__init__(*args, **kwargs)
        self.caller = kwargs.get('report', None)
        #if self.report: del kwargs['report']
        
        
    
    def compile_js(self, uri, args={}):
        try:
            template = settings.VIEWS.get_template(uri)
            return Code(template.render(**args))
        except Exception as e:
            self.logger.exception(e)
            pass
    
    def display(self, view='html'):
        try:
            gs = GridFS(self.__conn__['hotspot'], 'report_output')
            id = getattr(self, view)()
            file = gs.get(id)
            st = file.read()
            return st
        except Exception as e:
            self.logger.exception(e)
            raise e
    
    #accepts an array of dicts
    #always return the filename
    def csv(self):
        if not self.csv_output:
            gs = GridFS(self.__conn__['hotspot'], 'report_output')        
            filename = "%s-%s.csv" % (util.slugify(self.field('report')().name), util.slugify(util.format_date(self.completed)))
            file = gs.new_file(content_type='text/csv', encoding='utf-8', filename=filename)
            file.write(u'\ufeff'.encode('utf8'))
            if len(self.result): 
                keys = sorted(self.result[0].keys())
                uw = DictUnicodeWriter(file, keys)
                uw.writeheader()
                uw.writerows(self.result)
            
            file.close()
            self.csv_output = file._id
            self.save()
            return file._id
        else: return self.csv_output
    
    #accepts an array of dicts
    #always return the filename
    def html(self):
        if not self.html_output:
            gs = GridFS(self.__conn__['hotspot'], 'report_output')
            filename = "%s-%s.html" % (util.slugify(self.field('report')().name), util.slugify(util.format_date(self.completed)))
            header = []
            if len(self.result): header = sorted(self.result[0].keys())
            tb = TableBuilder(header, self.result)
            str = (('<h2>' + self.notes + '</h2><br><br>') if self.notes else '') + tb.render(id='report_output')
            id = gs.put(str, content_type='text/html', encoding='utf-8', filename=filename)
            self.html_output = id
            self.save()
            return id
        else: return self.html_output
    
    def pdf(self):
        #build PDF based on data
        pass
        
    def printable(self):
        #probably just use html
        pass
        
    
    def notify(self):
        #send emails to initiator and notifies
        pass
    
    def queue(self, session, params):
        self.status = 'IDLE'
        self.requested_by = session.user
        self.requested = datetime.datetime.utcnow()
        self.save()
        return self.run(params)
    
    def run(self, params=None):
        start = time.time()
        self.started = datetime.datetime.utcnow()
        self.params = self.parse_params(params)
        self.status = 'IN_PROGRESS'
        self.save()
        try:
            data = self.compile(self.params)
            self.result = data
            self.completed = datetime.datetime.utcnow()
            self.status = 'COMPLETE'            
        except Exception as e:
            self.logger.exception(e)
            self.result = str(e)            
            self.completed = datetime.datetime.utcnow()
            self.status = 'ERROR'            
            pass
        
        self.run_time = time.time()-start
        self.notify()
        self.save()
        return True
    
    #override!
    def parse_params(self, params):
        return params
    
    #override for paramters ui
    def parameters(self):
        self.logger.debug(self.caller)
        return self.render(template=self.parameters_template, args={'report':self.caller})
    
    #override this class in extending classes, return array of dicts   
    def compile(self, params=None):
        out = "tmp.%s" % ObjectId()
        map = self.compile_js(self.map, args={})
        reduce = self.compile_js(self.reduce, args={})
        finalize = self.compile_js(self.finalize, args={})
        query = {}
        return [row for row in self.__conn__['spoton']['history'].map_reduce(map, reduce, finalize=finalize, query=query, out=out, keeptemp=False)]

    
class Report(Model):
    __fieldorder__ = ('name', 'description', 'avg_runtime', 'completions', 'errors', 'generator')
    __db__ = "hotspot"
    __collection__ = "reports"    
    
    name = field.Char(required=True, widget=widget.TextInput, label="Name", min=2, max=200)
    description = field.Char(widget=widget.TextArea, label="Description")
    avg_runtime = field.Float(label='Average Runtime', disabled=True)
    completions = field.Integer(label='Completions', disabled=True)
    errors = field.Integer(label='Errors', disabled=True)
    occurences = relationship.Lazy(type=Generator, key='report')
    generator = field.Choice(label='Report Type (Generator)', choices=get_available_reports(), widget=widget.Select)
    
    def parameters_ui(self):
        cls = util.get_class('models.reports.%s.%s' % (self.generator.lower(), self.generator))
        return cls(report=self).parameters()
    
    def spawn(self, session, params):    
        cls = util.get_class('models.reports.%s.%s' % (self.generator.lower(), self.generator))
        gen = cls()
        gen.report = self.__id__
        try:
            return gen.queue(session, params)
        except Exception as e:
            self.logger.exception(e)
            self.__errors__.update(gen.errors)
            raise e
    
    def init(self, **kwargs):
        avg_runtime = 0
        completions = 0
        errors = 0
        total_time = 0
        total = 0
        if self.__id__:
            for occur in self.occurences():
                total+=1
                if occur.status == 'COMPLETE':
                    completions+=1
                elif occur.status == 'ERROR':
                    errors+=1
                
                total_time+=occur.run_time
            self.avg_runtime = (total_time/total) if total_time > 0 else 0
            self.completions = completions
            self.errors = errors
        
        
Generator.report = field.MongoId(type=Report, label='Report')
