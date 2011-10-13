import libraries
import tornado.web
import tornado.escape
from libraries import JsonEncoders
from system.jsonobject import JSONObject
import system.util as util
from system.session import Session
import settings

settings.SESSION_TYPE = Session


class BaseHandler(tornado.web.RequestHandler):
    session = None
    controller = None
    method = None
    def __init__(self, *args, **kwargs):
        self.logger = settings.get_logger(settings.LOG, self.__class__.__name__)
        super(BaseHandler, self).__init__(*args, **kwargs)
           
    def get_current_user(self):
        id = self.get_secure_cookie(settings.SESSION_COOKIE)
        self.logger.debug("ID:%s" % id)
        self.session = settings.SESSION_TYPE(id=id)
        #util.SESSION = self.session
        tz = self.request.headers.get('LOCAL-TZ', 'UTC')
        self.logger.debug("TIMEZONE IS: %s" % tz)
        #util.TIMEZONE = util.ZONES[tz.upper()]
        self.logger.debug("LOGGED IN: %s" % self.session.logged_in)
        return self.session.logged_in
        

class MainHandler(BaseHandler):
    
    def parse_args(self, args):
        dic = {}
        l = args[1:].split("/")
        for i in range(0, len(l), 2):
            try:
                if not l[i].strip() == "": dic[l[i]] = [l[i+1]]
            except:
                dic[l[i]] = [None]
        self.request.arguments.update(dic)
    
    protected = ('controller', 'method', 'form', 'callback_key', 'callback_data', 'identifier')
    
    def get(self, controller=None, method=None, *args):
        print controller
        print method
        print args
        try:
            self.logger.debug(controller)
            self.controller = controller
            self.method = method
            #self.parse_args(args[0])
            res = self.handle_request()
            self.write(res['result'])
        except Exception as e:
            self.logger.exception(e)
            self.write(str(e))
    
    def handle_request(self):
        try:
            cont = self.controller if self.controller else self.get_argument('controller', settings.DEFAULT_CONTROLLER)
            method = self.method if self.method else self.get_argument('method', settings.DEFAULT_METHOD)
            callback_key = self.get_argument('callback_key', None)
            callback_data = self.get_argument('callback_data', None)
            identifier = self.get_argument('identifier', None)
            kls = util.get_class('controllers.%s.%s' % (cont.lower(), cont.capitalize()))
            ars = {}
            print self.request.arguments.items()
            for key,val in self.request.arguments.items():
                if key not in self.protected: 
                    if len(val) > 1: ars[key]= val
                    else: ars[key]= val[0]
                elif key == 'form':
                    form = tornado.escape.json_decode(val[0])
                    ars['form'] = form        
            inst = kls(session=self.session, server=self)
            if inst.check_permissions(method): res = getattr(inst, method)(**ars)
            return {"identifier":identifier, "callback_key":callback_key, "result":res, 'callback_data':callback_data}
        except Exception as e:
            self.logger.exception(e)
            raise e
    
    
    def post(self, controller=None, method=None, *args):
        try:
            self.controller = controller
            self.method = method
            res = self.handle_request()
            if isinstance(res['result'], JSONObject): 
                res['identifier'] = res['result'].identifier if res['result'].identifier else res['identifier']
                res['result'].identifier = res['identifier'] if res['result'].identifier == None else res['result'].identifier
            ret = tornado.escape._json_encode(res, cls=JsonEncoders.ComplexEncoder)
            self.write(ret)
        except Exception as e:
            self.logger.exception(e)
            self.write(str(e))


class CallbackHandler(BaseHandler):
    def post(self, method):
        try:
            kls = util.get_class('controllers.callback.Callback')
            data = tornado.escape.json_decode(self.request.body)
            self.logger.debug("CALLBACK SESSION ID: %s " % data['session_id'])
            session = settings.SESSION_TYPE(id=data['session_id'])
            inst = kls(session=session)
            res = getattr(inst, method)(result=data)
            return True
        except Exception as e:
            self.logger.exception(e)
            self.write("bad callback")

class EmailHandler(BaseHandler):
    def post(self):
        try:
            kls = util.get_class('controllers.merchants.Merchants')
            inst = kls(session=None)
            ars = {}
            for key,val in self.request.arguments.items(): 
                n_k = key.replace("-", "_")
                if len(val) > 1: ars[n_k]= val
                else: ars[n_k]= val[0]
            self.logger.debug(ars)
            res = inst.incoming_email(**ars)
            self.logger.debug(res)
            self.write("thanks ;)")
        except Exception as e:
            self.logger.exception(e)
            self.write("We got some bad data :(")

class ISOHandler(BaseHandler):
    def post(self, method):
        try:
            kls = util.get_class('controllers.iso.%s.%s' % (method, method.capitalize()))
            inst = kls(session=None)
            self.logger.debug(self.request.body)
            res = getattr(inst, 'incoming')(data=self.request.body)
            self.logger.debug("good data from %s " % method)
            self.write(tornado.escape._json_encode(res, cls=JsonEncoders.ComplexEncoder))
        except Exception as e:
            self.logger.exception(e)
            self.write("something went horribly wrong")
            
class LogoutHandler(BaseHandler):
    def get(self):
        self.clear_cookie(settings.SESSION_COOKIE)
        self.redirect(settings.BASE_URL + "/login/")

class LoginHandler(BaseHandler):
    def get(self):
        popup = self.get_argument("popup", None)
        self.logger.debug(popup)
        kls = util.get_class("controllers.login.Login")
        inst = kls(session=self.session)
        if not popup:
            self.write(inst.login())
        else:
            self.write(tornado.escape._json_encode(inst.login_pop(), cls=JsonEncoders.ComplexEncoder))
    
    def post(self):
        session = Session()
        self.logger.debug(self.get_argument("username"))
        if session.login(self.get_argument("username"), self.get_argument("password")):
            self.logger.debug("Valid username and password!")
            self.set_secure_cookie(settings.SESSION_COOKIE, str(session.__id__), expires_days=2)    
            self.logger.debug(settings.BASE_URL + "/" + self.get_argument("redirect", ""))
            self.redirect(settings.BASE_URL + "/" + self.get_argument("redirect", ""))
        else:
            self.logger.debug("BAD USERNAME and PASSWORD")
            self.redirect(settings.BASE_URL + "/login/")
