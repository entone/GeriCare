from libraries.USTimeZone import *

class DateFormatter(object):
    def __init__(self, date, format="%a %b %d, %I:%M%p", timezone=Central):
        if isinstance(date, datetime):
            self.tz = timezone
            self.date = datetime(year=date.year, month=date.month, day=date.day, hour=date.hour, minute=date.minute, second=date.second, microsecond=date.microsecond, tzinfo=UTC)
            self.format = format
        else:
            self.date = None
        
    def __str__(self):
        if self.date:
            return self.date.astimezone(self.tz).strftime(self.format)
        return ""
        
    def __unicode__(self):
        return u"%s" % self.__str__()
