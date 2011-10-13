import unicodedata
import re
from libraries.DateFormatter import DateFormatter
from libraries.USTimeZone import *

def get_class(kls):
    parts = kls.split('.')
    module = ".".join(parts[:-1])
    m = __import__(module)
    for comp in parts[1:]:
        m = getattr(m, comp)            
    return m

ZONES = {
    'UTC':UTC,
    'EST':Eastern,
    'EDT':Eastern,
    'CST':Central,
    'CDT':Central,
    'MST':Mountain,
    'MDT':Mountain,
    'PST':Pacific,
    'PDT':Pacific
}

TIMEZONE = Central

def format_date(date, format="%a %b %d %Y, %I:%M%p"):
    if date: return DateFormatter(date, format, timezone=TIMEZONE) 
    return 'NA'

_slugify_strip_re = re.compile(r'[^\w\s-]')
_slugify_hyphenate_re = re.compile(r'[-\s]+')
def slugify(value):
    if not isinstance(value, unicode):
        value = unicode(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore')
    value = unicode(_slugify_strip_re.sub('', value).strip().lower())
    return _slugify_hyphenate_re.sub('-', value)


import re
urlfinder = re.compile('^(http:\/\/\S+)')
urlfinder2 = re.compile('\s(http:\/\/\S+)')
def linkify(value, extra):
    value = urlfinder.sub(r'<a href="\1" %s>\1</a>' % extra, value)
    return urlfinder2.sub(r' <a href="\1" %s>\1</a>' % extra, value)
