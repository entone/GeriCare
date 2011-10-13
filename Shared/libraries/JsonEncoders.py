import json
import datetime
import time
from pymongo.objectid import ObjectId

class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime): return (time.mktime(obj.timetuple())+(obj.microsecond/1000000.0))*1000
        if isinstance(obj, ObjectId): return str(obj)
        if isinstance(obj, Exception): return str(obj)
        try: return obj.json()
        except Exception as e: pass