import json
from pymongo.connection import Connection
import datetime

class Parser(object):
    
    def __init__(self, file):
        self.conn = Connection('localhost:27017')
        self.db = self.conn['gericare']
        self.collection = self.db['locations']
        #self.collection.ensure_index({"state":1, "provider_number":1})
        self.file = file
        self.parse()
    
    def parse(self):
        self.data = json.loads(open(self.file).read())
        self.cols = self.data['meta']['view']['columns']
        self.points = []
        for nh in self.data['data']:
            home = {}
            for i, data in enumerate(nh):
                type = self.cols[i]['dataTypeName']
                name = self.cols[i]['fieldName']
                #print type
                #print name
                try:
                    data = getattr(self, "parse_%s"%type)(data, field=name)
                except Exception as e: 
                    print e
                home[name] = data
            self.points.append(home)
            self.collection.insert(home)
        
        
    def parse_date(self, data, field=None):
       try:
           return datetime.datetime.strptime(str(data), "%Y%m%d")
       except:
           return datetime.datetime.utcfromtimestamp(data) 
    
    def parse_number(self, data, field=None):
        return int(data)
    
    def replace(self, st, dic):
        for k,v in dic.iteritems(): st = st.replace(k, v)
        return st
    
    def parse_text(self, data, field=None):
        if field == 'phone_number': return u"+1%s" % self.replace(data, {"(":"", ")":"", " ":"", "-":""}).strip()
        if field == 'state': return data.upper()
        final = " ".join([s.capitalize() for s in data.lower().strip().split(" ")])
        return u"%s" % final
    
    def parse_html(self, data, field=None): 
        return self.parse_text(data, field=field)
    
    def parse_checkbox(self, data, field=None): return bool(data)
        
pa = Parser("data/nursing_homes.json")
print pa.points
