import json
from libraries import JsonEncoders

class JSONObject(object):
    success = False
    html = ""
    identifier = ""
    action=""
    callback=""
    data = {}
    finalize = None
    def __init__(self, success=False, html="", identifier=None, action="", callback="", data={}, finalize=None):
        self.success = success
        self.html = html
        self.identifier = identifier
        self.action = action
        self.callback = callback
        self.data = data
        self.finalize = finalize
        
    def json(self):
        return json.dumps({"success":self.success, "html":self.html, "identifier":self.identifier, "action":self.action, "callback":self.callback, "data":self.data, 'finalize':self.finalize}, cls=JsonEncoders.ComplexEncoder)
