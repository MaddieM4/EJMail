class Conversation(object):
    def __init__(self, name, *participants):
        self.name = name
        self.participants = list(participants)
        self.messages = {}

    def register_message(self, message):
        self.messages[message.id] = message
        self.on_message(message)

    def on_message(self, message):
        '''
        Callback for recieving messages.
        '''
        pass
