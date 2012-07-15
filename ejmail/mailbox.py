from ejtp.router import Router
from dbcps.storage import Storage
from message import Message
from conversation import Conversation

class Mailbox(object):
    '''
    Class for persistent mail storage.

    >>> m = Mailbox(['udp4', ['localhost',9898], 'ejmail-test'])
    >>> m.interface
    ['udp4', ['localhost', 9898], 'ejmail-test']
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
        self.cpsdesc = cpsdesc or ('ramdict', ['rotate', 0])
        self.storage = Storage([self.cpsdesc])
        self.conversations = {}

    def recv(self, data):
        '''
        >>> m = Mailbox(['udp4', ['localhost',9898], 'ejmail-test'])
        >>> m.add_conversation("Demonstration")
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
        if convo in self.conversations:
            self.conversations[convo].register_message(message)

    def add_conversation(self, name, *participants):
        self.conversations[name] = Conversation(name, *participants)
