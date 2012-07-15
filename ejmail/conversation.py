class Conversation(object):
    def __init__(self, name):
        self.name = name
        self.messages = {}

    def register_message(self, message):
        self.messages[message.hash] = message
        self.on_message(message)

    def on_message(self, message):
        '''
        Callback for recieving messages.
        '''
        pass
