from libraries.USTimeZone import *

class DateFormatter(object):
    def __init__(self, date, format="%a %b %d, %I:%M%p", timezone=Central):
        self.tz = timezone
        self.date = datetime(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute, second=date.second, microsecond=date.microsecond, tzinfo=UTC)
        self.format = format
        
    def __str__(self):
        return self.date.astimezone(self.tz).strftime(self.format)
        
    def __unicode__(self):
        return u"%s" % self.__str__()