import csv, cStringIO, codecs

class DictUnicodeWriter(object):

    def __init__(self, f, fieldnames, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.fieldnames = [x for x in fieldnames if x!='!id']
        self.queue = cStringIO.StringIO()
        self.writer = csv.DictWriter(self.queue, self.fieldnames, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, D):
        obj = {}
        if D.has_key('!id'): del D['!id']
        for k,v in D.iteritems():
            if isinstance(v, (str, unicode)):obj[k] = v.encode("utf-8")
            else: obj[k] = v
        self.writer.writerow(obj)
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for D in rows:
            self.writerow(D)

    def writeheader(self):
        header = {}
        for v in self.fieldnames:
            header[v] = v.split('~')[-1]
        self.writer.writerow(header)
