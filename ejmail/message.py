from ejtp.util import hasher

class Message(object):
    def __init__(self, data):
        self.data = data
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
