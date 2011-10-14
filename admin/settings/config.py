import os, logging, logging.handlers
import libraries
import uuid
from mako.lookup import TemplateLookup
from libraries.cloghandler import ConcurrentRotatingFileHandler

PROJECT = "GeriCare Admin"
VERSION_INFO = (1, 0, 0)
VERSION = '.'.join(str(n) for n in VERSION_INFO[:3])

def is_dev():
    file = os.path.abspath(os.path.dirname(__file__))+"/../DEV"
    return os.path.exists(file)
    
def is_local():
    file = os.path.abspath(os.path.dirname(__file__))+"/../LOCAL"
    return os.path.exists(file)
    
def is_deployed():
    return str(__file__).startswith('/home/entone/webapps/')
    
def startup():
    try:
        print "Running Start UP!"
        import settings.startup
    except Exception as e: 
        print e
        
SESSION_COOKIE = "geri-session_id"

BASE_URL = "/admin" if is_deployed() else ""
STATIC_FILES = "/admin/static" if is_deployed() else "/static"

DB = 'gericare'
SERVER_PORT = 39304

ADMIN_DB = 'gericare'

LOG = "admin"

ROOT = os.path.abspath(os.path.dirname(__file__))+"/../"

v = ROOT+"templates"
VIEWS = TemplateLookup(directories=[v,], output_encoding='utf-8', input_encoding='utf-8', encoding_errors='replace')
    
loggers = {}

LOG_SIZE = 100*1048576
LOG_CACHE = 10

def get_logger(mod, sub=None):
    mod = mod.lower()
    ns = sub if sub else mod
    if loggers.has_key(ns): return loggers[ns]
    logger = logging.getLogger(ns)
    logger.setLevel(logging.DEBUG)
    hndlr = ConcurrentRotatingFileHandler("%s/logs/%s" % (ROOT, "%s.log" % mod), maxBytes=LOG_SIZE, backupCount=LOG_CACHE)
    formatter = logging.Formatter('%(thread)d | %(asctime)s:%(levelname)s:%(name)s:%(lineno)s: %(message)-80s')
    hndlr.setFormatter(formatter)
    logger.addHandler(hndlr)
    loggers[ns] = logger
    return loggers[ns]

if is_dev():
    DYNAMIC_EMAIL = "gericare.mailgun.org"
    if is_local(): MONGO_HOSTS = 'localhost:27017'
    else: MONGO_HOSTS = 'localhost:28556'
else:
    DYNAMIC_EMAIL = "gericare.mailgun.org"
    MONGO_HOSTS = 'localhost:28556'

DEFAULT_CONTROLLER = "Locations"
DEFAULT_METHOD = "index"

SERVER_SETTINGS = {
    "static_path": ROOT+"/static",
    "cookie_secret": "!!!!!!!!!!!gericarecausewecare!!!!!!!",
    "login_url": "%s/login/" % BASE_URL,
}

