import settings, datetime, time, threading, libraries, datetime, sys, locale
from apscheduler.triggers import SimpleTrigger, IntervalTrigger, CronTrigger
from system.memory_monitor import MemoryMonitor
from system.model import Model
import system.helpers as helpers
import system.util as util
import humongolus.field as field

try:
    import cPickle as pickle
except ImportError:  # pragma: nocover
    import pickle

try:
    from bson.binary import Binary
except ImportError:  # pragma: nocover
    raise ImportError('Polling requires PyMongo installed')



class Poll(threading.Thread, Model):
    __db__ = "polling"
    __collection__ = 'polls'
    IDLE = 'IDLE'
    RUNNING = 'RUNNING'
    
    trigger = field.Field()
    name = field.Char()
    args = field.Field()
    last = field.Date()
    next = field.Date()
    module = field.Char()
    project = field.Char()
    cls = field.Char()
    last_error = field.Field()
    completions = field.Integer(default=0)
    errors = field.Integer(default=0)
    status = field.Choice(choices=['IDLE', 'RUNNING'], default='IDLE')
    
    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = True
        super(Model, self).__init__(*args, **kwargs)
    
    def run(self):
        try:
            self.logger.debug("Running: %s" % self.name)
            res = self.__conn__[self.__db__].command('findandmodify', self.__collection__, query={'_id':self.__id__, 'status':self.IDLE}, update={'$set':{'status':self.RUNNING}}, upsert=False)           
            if res:
                res = res['value']
                trig = pickle.loads(res['trigger'])
                try:
                    cls = util.get_class("%s.%s" % (res['module'], res['cls']))
                    me = cls(id=self.__id__)
                    if self.args: res = me.work(**self.args) 
                    else: res = me.work()
                    me.last = datetime.datetime.utcnow()
                    me.next = trig.get_next_fire_time(me.last)
                    me.completions+=1
                    me.status = self.IDLE
                    me.save()
                    return True
                except Exception as e:
                    me.last = datetime.datetime.utcnow()
                    me.next = trig.get_next_fire_time(me.last)
                    me.errors+=1
                    me.last_error = e.message
                    me.status = self.IDLE
                    me.save()
                    self.logger.exception(e)
                    return False
        except Exception as e: 
            self.logger.exception(e)
            pass
    
    
    def work(self, **kwargs): pass
    
    def render(self, uri, args={}):
        try:
            template = settings.VIEWS.get_template(uri)
            args['DateFormatter'] = util.format_date
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
    
    
    def get_trigger(self, weeks=0, days=0, hours=0, minutes=0, seconds=0, start_date=None):
        interval = datetime.timedelta(weeks=weeks, days=days, hours=hours, minutes=minutes, seconds=seconds)
        return IntervalTrigger(interval, start_date)

    @classmethod
    def add(cls, poll, **kwargs):
        try:
            res = cls.find_one(query={'name':poll.name})
            trig = poll.get_trigger(**kwargs)
            next = kwargs.get('start_date', datetime.datetime.utcnow())
            bin = Binary(pickle.dumps(trig, pickle.HIGHEST_PROTOCOL))
            if not res:
                poll.module = sys.modules[poll.__module__].__name__
                poll.project = settings.PROJECT
                poll.cls = poll.__class__.__name__
                poll.next = trig.get_next_fire_time(next)
                poll.trigger = bin
                poll.save()
            else:
                res.next = trig.get_next_fire_time(next)
                res.trigger = bin
                res.save()
        except Exception as e:
            print e
            pass
    
    @classmethod
    def register(cls, **kwargs):
        print "Registering: %s with: %s" % (cls.__name__, kwargs)
        p = cls()
        p.name = cls.__name__
        cls.add(p, **kwargs)
        
        
        
class IntervalPoll(Poll): pass
      
class CronPoll(Poll):
    
    def get_trigger(self, year=None, month=None, day=None, week=None, day_of_week=None, hour=None, minute=None, second=None, start_date=None):
        return CronTrigger(year=year, month=month, day=day, week=week, day_of_week=day_of_week, hour=hour,minute=minute, second=second, start_date=start_date)
        
class DatePoll(Poll):
    
    def get_trigger(self, date=None, start_date=None):
        print date
        return SimpleTrigger(date)


class Polling(threading.Thread):
    
    running = False
    
    def __init__(self, project=None):
        super(Polling, self).__init__()
        self.project = project
        self.daemon = True
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        self.memory = MemoryMonitor()
    
    def run(self):
        self.running = True
        self.init_memory = self.memory.usage()
        self.logger.debug("Init Memory: %s" % self.init_memory)
        while self.running:
            try:
                self.start_memory = self.memory.usage()
                polls = self.get_polls()
                if polls:
                    #print polls.count()
                    self.logger.debug("Running %s polls" % polls.count())
                    for p in polls: p.start()
            except Exception as e:
                print e
                self.logger.exception(e)
            self.end_memory = self.memory.usage()
            self.logger.debug("Current Threads: %s" % threading.active_count())
            self.logger.debug("Current Memory: %s" % self.end_memory)
            time.sleep(1)
            
    def get_polls(self):
        try:
            now = datetime.datetime.utcnow()
            qu = {'status':Poll.IDLE, "next":{"$lte":now}, 'project':self.project}
            polls = Poll.find(query=qu)
            return polls
        except Exception as e:
            self.logger.exception(e)

