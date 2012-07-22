from ejtp.router import Router
from ejtp.client import Client
from dbcps.storage import Storage
from message import Message
from conversation import Conversation

class Mailbox(object):
    '''
    Class for persistent mail storage.

    >>> m = Mailbox(['udp4', ['localhost',9001], 'ejmail-test'])
    >>> m.interface
    ['udp4', ['localhost', 9001], 'ejmail-test']
    >>> m.router #doctest: +ELLIPSIS
    <ejtp.router.Router object at ...>
    >>> m.cpsdesc
    ('ramdict', ['rotate', 0])
    >>> m.storage #doctest: +ELLIPSIS
    <dbcps.storage.Storage object at ...>
    '''
    def __init__(self, interface, router=None, cpsdesc=None):
        self.interface = interface
        self.router = router or Router()
        self.client = Client(self.router, self.interface)
        self.cpsdesc = cpsdesc or ('ramdict', ['rotate', 0])
        self.storage = Storage([self.cpsdesc])
        self.conversations = {}

    def recv(self, data):
        '''
        >>> m = Mailbox(['udp4', ['localhost',9002], 'ejmail-test'])
        >>> m.add_conversation("Demonstration") # Add ahead of time so we can set callback
        >>> def msgcallback(msg):
        ...     print msg.hash
        ...     print msg.content
        >>> m.conversations["Demonstration"].on_message = msgcallback
        >>> m.recv({'conversation':'Demonstration', 'content':'Demo content'})
        306bdbd690d9910acf002ea6dc25cf6440ae6c85
        Demo content
        '''
        message = Message(data)
        convo = message.conversation
        self.add_conversation(convo)
        convo_obj = self.conversations[convo]
        convo_obj.register_message(message)
        convo_obj.on_message(message)
        self.storage[message.hash] = str(message)

    def add_conversation(self, name):
        if not name in self.conversations:
            self.conversations[name] = Conversation(name)
