import libraries, json, random
import settings
import humongolus.widget as widget
import system.util as util
import datetime

class DateCtrl(widget.Date):
    
    def render(self, **kwargs):
        rand_id = random.randint(2000, 9999999)
        kwargs['value'] = self.__field__.__value__.strftime("%b-%d-%Y") if self.__field__.__value__ else ""
        kwargs['id'] = "id_%s%s" % (self.__field__.name, rand_id)
        r = super(DateCtrl, self).render(**kwargs)
        script = """
<script>
$(function() {
$( "#%s" ).datepicker({dateFormat:'M-dd-yy'});
});
</script> """ % self.__args__['id']
        return script + r

    def __clean__(self, value):
        try:
            return super(DateCtrl, self).__clean__(value)
        except:
            try:
                return datetime.datetime.strptime(value, "%b-%d-%Y")
            except:
                ex = Exception(u'The value given is not a valid datetime')
                self.__error__ = ex
                raise ex
