import json
from pymongo.connection import Connection
import datetime
import re, htmlentitydefs

##
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)

class Parser(object):
    
    def __init__(self, file):
        self.conn = Connection('localhost:27017')
        self.db = self.conn['gericare']
        self.collection = self.db['locations']
        self.file = file
        self.parse_enforcements()
    
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
                except Exception as e:pass 
                home[name] = data
            #self.points.append(home)
            print "Saving: %s" % home['nursing_home_name']
            self.collection.insert(home)
        
        self.parse_ratings()
        #self.parse_definciencies()
        #self.parse_enforcements()
        self.parse_staff()
        
        
    def parse_date(self, data, field=None):
       try:
           return datetime.datetime.strptime(str(data), "%Y%m%d")
       except:
           return datetime.datetime.utcfromtimestamp(data) 
    
    def parse_number(self, data, field=None, typ=int):
        return typ(data)
        
    def parse_provider(self, data, field=None):
        return data
    
    def replace(self, st, dic):
        for k,v in dic.iteritems(): st = st.replace(k, v)
        return st
    
    def parse_text(self, data, field=None):
        if field == 'phone_number': return u"+1%s" % self.replace(data, {"(":"", ")":"", " ":"", "-":""}).strip()
        if field == 'state': return data.upper()
        if field == 'enforcement_type': return data.upper()
        final = " ".join([s.capitalize() for s in data.lower().strip().split(" ")])
        return u"%s" % final
    
    def parse_html(self, data, field=None):
        data = unescape(data)
        return self.parse_text(data, field=field)
    
    def parse_checkbox(self, data, field=None): return bool(data)
    
    def parse_money(self, data, field=None):
        try:
            return float(data)
        except:return data
    
    def parse_ratings(self):
        obj = json.loads(file("data/ratings.json").read())
        cols = obj['meta']['view']['columns']
        for rt in obj['data']:
            ratings = {}
            for i, data in enumerate(rt):
                if cols[i]['fieldName'] == 'provider_number':
                    pn = data
                if cols[i]['dataTypeName'] == 'stars':
                    try:
                        data = int(data)
                    except:pass
                        
                    ratings[cols[i]['fieldName']] = data
            print "Adding Ratings for: %s %s" % (pn, ratings)
            self.collection.update({"provider_number":pn}, {"$set":{"ratings":ratings}})
    
    def parse_deficiencies(self):
        obj = json.loads(file("data/deficiencies.json").read())
        cols = obj['meta']['view']['columns']
        for com in obj['data']:
            complaint = {"survey_date":None, "date_of_correction":None, "deficiency_type":None, "deficiency_category":None, "deficiency":None, "scope":None, "level_of_harm":None}
            for i, data in enumerate(com):
                if cols[i]['fieldName'] == 'provider_number': pn = data
                try:
                    print complaint[cols[i]['fieldName']]
                    complaint[cols[i]['fieldName']] = getattr(self, "parse_%s"%cols[i]['dataTypeName'])(data=data, field=cols[i]['fieldName'])
                except Exception as e:pass
            id = self.collection.find_one({"provider_number":pn}, {"_id":1})
            complaint['location'] = id['_id']
            self.db['deficiencies'].insert(complaint)
    
    def parse_enforcements(self):
        obj = json.loads(file("data/enforcement_dates.json").read())
        cols = obj['meta']['view']['columns']
        for com in obj['data']:
            complaint = {"enforcement_type":None, "civil_money_penalty":None, "survey_date":None}
            for i, data in enumerate(com):
                if cols[i]['fieldName'] == 'provider_number': pn = data
                try:
                    print complaint[cols[i]['fieldName']]
                    complaint[cols[i]['fieldName']] = getattr(self, "parse_%s"%cols[i]['dataTypeName'])(data=data, field=cols[i]['fieldName'])
                except Exception as e:pass
            id = self.collection.find_one({"provider_number":pn}, {"_id":1})
            complaint['location'] = id['_id']
            self.db['enforcements'].insert(complaint)
    
    def parse_staff(self):
        obj = json.loads(file("data/staff.json").read())
        cols = obj['meta']['view']['columns']
        for com in obj['data']:
            complaint = {"number_of_residents":None, "number_of_rn_hours_per_resident_per_day":None, "number_of_lpn_lvn_hours_per_resident_per_day":None, 
            "total_number_of_licensed_staff_hours_per_resident_per_day":None, "number_of_cna_hours_per_resident_per_day":None}
            for i, data in enumerate(com):
                if cols[i]['fieldName'] == 'provider_number': pn = data
                try:
                    print complaint[cols[i]['fieldName']]
                    if cols[i]['dataTypeName'] == 'number':
                        data = getattr(self, "parse_%s"%cols[i]['dataTypeName'])(data=data, field=cols[i]['fieldName'], typ=float)
                        complaint[cols[i]['fieldName']] = data
                        #print data
                    else: 
                        complaint[cols[i]['fieldName']] = getattr(self, "parse_%s"%cols[i]['dataTypeName'])(data=data, field=cols[i]['fieldName'])
                except Exception as e:pass
            
            print "Adding Staffing for: %s %s" % (pn, complaint)
            self.collection.update({"provider_number":pn}, {"$set":{"staffing":complaint}})
            
    
        
            
        
            
            
    
    
pa = Parser("data/nursing_homes.json")
