from system.view import View

class LocationTable(View):
    columns = [
        {
            'key':'nursing_home_name',
            'display':"Name"
        },
        {
            'key':'city',
            'display':"City"
        },
        {
            'key':'phone_number',
            'display':"Phone"
        },
        {
            'key':'actions',
            'display':'Actions'
        }
    ]
    _template = 'models/location/table.html'
    
    
class LocationForm(View):
    _template = 'models/location/form.html'
    
class LocationNewForm(View):
    _template = 'models/location/form.html'
