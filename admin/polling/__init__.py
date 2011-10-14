import settings, datetime, locale
from system.polling import Polling

locale.setlocale(locale.LC_ALL, '')

TEST = False

if not settings.is_local() or TEST:    
    #p = Polling(project=settings.PROJECT)
    #p.start()
    pass
    


