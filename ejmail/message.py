class Message(object):
    def __init__(self, data, id=0):
        self.data = data
        self.id = id

    @property
    def content(self):
        return self.data['content']

    @property
    def conversation(self):
        return self.data['conversation']

    @property
    def timecode(self):
        return self.data['timecode']
