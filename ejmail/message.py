from ejtp.util import hasher
import datetime, dateutil.parser

class Message(object):
    def __init__(self, data):
        self.data = data
        if not 'timecode' in self.data:
            self.data['timecode'] = datetime.datetime.now().isoformat()
        self.hash = hasher.checksum(data)

    def __str__(self):
        return hasher.strict(self.data)

    @property
    def content(self):
        return self.data['content']

    @property
    def conversation(self):
        return self.data['conversation']

    @property
    def timecode(self):
        return self.data['timecode']

    @property
    def datetime(self):
        return dateutil.parser.parse(self.timecode)
