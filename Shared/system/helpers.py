import settings

def static_url(file):
    return "%s/%s?v=%s" % (settings.STATIC_FILES, file, settings.VERSION)
    
def absolute_url(uri):
    return "%s/%s" % (settings.BASE_URL, uri)