class Conversation(object):
    def __init__(self, name):
        self.name = name
        self.messages = {}

    def register_message(self, message):
        self.messages[message.hash] = message

    def timeline(self):
        '''
        All messages organized chronologically, oldest first.
        '''
        messages = self.messages.values()
        def getdatetime(msg): return msg.datetime
        messages.sort(key=getdatetime)
        return messages

    def on_message(self, message):
        '''
        Callback for recieving messages.
        '''
        pass
