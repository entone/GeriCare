import settings, copy
        
def escape(s):
    orig = copy.copy(s)
    try:
        s = unicode(s)
        return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')
    except: return orig


def sequence(field=None):
    field = field if field else "inc_id"
    res = settings.CONNECTION[settings.AUTO_INCREMENT_DB].command("findandmodify", "sequence", query={field:{'$exists':True}}, update={'$inc':{field:1}}, new=True, upsert=True)
    return res['value'][field]