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
import system.util as util



logger.info('Starting %s version %s' % (settings.PROJECT, settings.VERSION))

try:
    port = sys.argv[1]
except:
    port = settings.SERVER_PORT

s = Server(port=port)
