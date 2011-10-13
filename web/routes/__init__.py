import libraries
import tornado.web
from system.handlers import *


ROUTES = [
    tornado.web.URLSpec(r"/login/?", LoginHandler, name="Login"),
    tornado.web.URLSpec(r"/logout/?", LogoutHandler, name="Logout"),
    tornado.web.URLSpec("/callback/([a-z\-_]+)?/?", CallbackHandler, name="Callback"),
    tornado.web.URLSpec("/email/?", EmailHandler, name="Email"),
    tornado.web.URLSpec(r"/([a-z-]+)/?([a-z\-_]+)?/?", MainHandler, name="Main"),
    tornado.web.URLSpec("/", MainHandler, name="MainNoURL"),
]
