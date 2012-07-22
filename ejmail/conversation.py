class Conversation(object):
    def __init__(self, name):
        self.name = name
        self.messages = {}
        self.uniques = {}

    def register_message(self, message):
        self.messages[message.hash] = message

    def on_message(self, message):
        '''
        Callback for recieving messages.
        '''
        pass
