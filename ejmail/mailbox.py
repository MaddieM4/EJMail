from ejtp.router import Router
from ejtp.client import Client
from ejtp import address

from dbcps.storage import Storage

from message import Message
from conversation import Conversation

import json

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
        self.client.rcv_callback = self.rcv_callback
        self.cpsdesc = cpsdesc or ('ramdict', ['rotate', 0])
        self.storage = Storage([self.cpsdesc])
        self.unread = {}
        self.conversations = {}

    def recv(self, data, addr=None):
        '''
        Interpret an email recieved through EJTP client.

        >>> m = Mailbox(['udp4', ['localhost',9002], 'ejmail-test'])
        >>> m.add_conversation("Demonstration") # Add ahead of time so we can set callback
        >>> def msgcallback(msg):
        ...     print msg.hash
        ...     print msg.content
        >>> m.conversations["Demonstration"].on_message = msgcallback
        >>> m.recv({'conversation':'Demonstration', 'content':'Demo content', 'timecode':'not an automatic one'})
        65d35f7482c0c610ada04ff4e7bf4fa66f4769dd
        Demo content
        '''
        message = Message(data)
        if addr:
            self.ack(message, addr)
        convo = message.conversation
        self.add_conversation(convo)
        convo_obj = self.conversations[convo]
        convo_obj.register_message(message)
        convo_obj.on_message(message)
        self.storage[message.hash] = str(message)

    def add_conversation(self, name):
        '''
        Set up a Conversation object for this mailbox.

        This is called by self.recv automatically.
        '''
        if not name in self.conversations:
            self.conversations[name] = Conversation(name)

    def rcv_callback(self, msg, client):
        '''
        Callback for EJTP client.

        TODO: Filter out messages where EJTP sender does not match "from" field.
        '''
        msg_dict = json.loads(msg.content)
        msg_type = msg_dict['type']
        msg_data = msg_dict['data']
        if msg_type == "ejmail-message":
            self.recv(msg_data, msg.addr)
        elif msg_type == "ejmail-mark":
            saddr = address.str_address(msg.addr)
            for hash in msg_data:
                del self.unread[saddr][hash]
            for unread in self.unread[saddr].values():
                self.send(unread, [('Retrying send...', saddr)])

    def send(self, msg, recipients=None):
        '''
        Send ejmail.message.Message object to its recipients.

        >>> import time
        >>> m3addr = ['udp4', ['localhost',9003], 'britta']
        >>> m4addr = ['udp4', ['localhost',9004], 'jeff']
        >>> m3 = Mailbox(m3addr)
        >>> m4 = Mailbox(m4addr)
        >>> m4.client.encryptor_cache = m3.client.encryptor_cache
        >>> m3.client.encryptor_set(m3addr, ['rotate', 5])
        >>> m3.client.encryptor_set(m4addr, ['rotate', -14])
        >>> msg = Message({
        ...     'to':[['Jeff Winger', m4addr]],
        ...     'from':['Britta Perry', m3addr],
        ...     'conversation':'Wazzaaaappp',
        ...     'content':"I'm druunnkkkk",
        ... })
        >>> m3.send(msg); time.sleep(0.1) #doctest: +ELLIPSIS
        UDPJack out: ...
        >>> m4.conversations.keys()
        [u'Wazzaaaappp']
        >>> m4.conversations['Wazzaaaappp'].timeline()[0].content
        u"I'm druunnkkkk"
        >>> m3.unread
        {'["udp4",["localhost",9004],"jeff"]': {}}
        '''
        convo = msg.conversation
        self.add_conversation(convo)
        convo_obj = self.conversations[convo]
        convo_obj.register_message(msg)
        recipients = recipients or msg.data['to']
        for recipient in recipients:
            name, addr = recipient
            self.client.write_json(address.py_address(addr), {
                'type':'ejmail-message',
                'data':msg.data,
            })
            saddr = address.str_address(addr)
            if not saddr in self.unread:
                self.unread[saddr] = {}
            self.unread[saddr][msg.hash] = msg

    def ack(self, message, addr):
        self.client.write_json(
            address.py_address(addr),
            {
                'type':'ejmail-mark',
                'data':[message.hash],
            }
        )
