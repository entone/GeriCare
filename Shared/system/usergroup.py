from system.model import Model
import humongolus.field as field
import humongolus.widget as widget

class UserGroup(Model):
    __db__ = "hotspot"
    __collection__ = "usergroups"
    __fieldorder__ = ('name', 'level')
    
    name = field.Char(required=True, label='Name')
    level = field.Integer(required=True, label='Level', max=10, min=1, default=1)