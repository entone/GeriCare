import settings

class TableBuilder(object):
    rows = []
    header = []
    footer = []
    is_merchant_report = False
    
    def __init__(self, header=[], rows=[], footer=[]):
        self.header = [x.split('~')[-1] for x in sorted(header) if x != '!id']
        self.rows = rows
        self.footer = footer
        self.is_merchant_report = '!id' in header
        
    def render(self, cls="", id=""):
        open_tag = "<table id='%s' class='%s'>" % (id, cls)
        header = "<thead><tr>%s</tr></thead>" % "".join(["<th>%s</th>" % h for h in self.header]) if len(self.header) else ""
        body = "<tbody>%s</tbody>" % "".join(["<tr id='%s' class='report_row'>%s</tr>" % (row.get('!id', ''), "".join(["<td>%s</td>" % v for k,v in iter(sorted(row.iteritems())) if k != '!id'])) for row in self.rows])
        footer = "<tfoot><tr>%s</tr></tfoot>" % "".join(["<td>%s</td>" % f for f in self.footer]) if len(self.footer) else ""
        close_tag = "</table>"
        absolute_url = "%s/%s" % (settings.BASE_URL, 'merchants/')
        javascript = "<script>$('#%s tr').click( function(){ window.location='%s?mid='+$(this).attr('id'); } );</script>" % (id,absolute_url) if self.is_merchant_report else ''
        return "%s%s%s%s%s%s" % (open_tag, header, footer, body, close_tag, javascript)
