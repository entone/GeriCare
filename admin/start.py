import sys, os

DIRNAME = os.path.abspath(os.path.dirname(__file__))
sys.path.append(DIRNAME+"/../Shared/")
sys.path.append(DIRNAME+"/../")

import settings
import libraries
import humongolus.settings as humsettings
from system.singleconnection import SingleConnection

logger = settings.get_logger(settings.LOG, "start")
logger.info("Database: %s" % settings.MONGO_HOSTS)

conn = SingleConnection(settings.MONGO_HOSTS)
humsettings.CONNECTION = conn
humsettings.AUTO_INCREMENT_DB = settings.DB
humsettings.LOG = settings.LOG
humsettings.LOGGER = settings.get_logger

from system.server import Server
from system.session import Session
from system.user import User
import system.util as util

logger.info('Starting %s version %s' % (settings.PROJECT, settings.VERSION))

conn[settings.ADMIN_DB]['change_log'].ensure_index([('reference.id',1), ('user', 1)])

conn[settings.ADMIN_DB]['users'].ensure_index([('username',1)], unique=True)

super = conn[settings.ADMIN_DB]['users'].find_one({'username':'super'})
if not super:
    super = User()
    super.username = 'super'
    super.firstName = "Super"
    super.lastName = "Admin"
    super.status = "Active"
    super.password = super.encrypt_password('abudabu')
    print super.save()
    ses = Session()
    ses.user = super
    
    
    print super.__errors__


try:
    port = sys.argv[1]
except:
    port = settings.SERVER_PORT

s = Server(port=port)
