import sys

from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application.internet import ClientService, backoffPolicy
from twisted.internet.endpoints import clientFromString
from twisted.logger import (Logger, LogLevel, globalLogBeginner, textFileLogObserver, FilteringLogObserver, LogLevelFilterPredicate)
from twisted.internet.protocol import Protocol, ClientFactory
from mqtt.client.factory import MQTTFactory
import random
import calendar
import time
import datetime
import itertools
import uuid

class MQTTProtocol(Protocol):

    def dataReceived(self, data):
        # print del payload che viene ricevuto dal client
        sys.stdout.write(data)

    def connectionMade(self):
        now = datetime.datetime.now()
        now = str(now.hour) + ":" + str(now.minute) + ":" + str(now.second)
        print("Connessione al server effettuata alle {} ({})".format(now, calendar.timegm(time.gmtime())))
        self.send_next_pdu()

    def send_next_pdu(self):
        try:
            self.send_pdu(self.current_session)
            reactor.callLater(5000//1000, self.send_next_pdu)
        except StopIteration:
            print("Fine della sessione")
            self.transport.loseConnection()

    def send_pdu(self, pdutype):
        from twisted.internet import reactor
        try:
            data = bytes('hello world', 'utf-8')
            print(data)
            self.transport.write(b'ciao?')
        except (IOError, OSError) as err:
            print("Errore {}".format(err))
            reactor.stop()

class MQTTClientFactory(ClientFactory):

    protocol = MQTTProtocol
    
    def __init__(self, reconnect=True, clientId=None, keepalive=None, qos=0, msg=None, retain=False):
        self.reconnect = reconnect
        self.clientId = clientId if clientId is not None else "client_" + str(random.randint(1, 2000))
        self.keepalive = keepalive if keepalive is not None else 1000
        self.qos = qos
        self.msg = msg
        self.retain = retain
        self.session_structures = [
            ["connect", 'subscribe', 'publish' "disconnect"]
        ]   
        self.session = itertools.cycle(iter(self.session_structures))

    def startedConnecting(self, connector):
        print("Connessione in corso")

    def buildProtocol(self, addr):
        protocol_instance = ClientFactory.buildProtocol(self, addr)
        protocol_instance.current_session = itertools.cycle(next(self.session))
        protocol_instance.session_id = str(uuid.uuid4())
        return protocol_instance

    def clientConnectionLost(self, connector, reason):
        print("Connessione persa, motivazione: {}".format(reason)) # motivazione della connessione persa
        if self.reconnect:
            connector.connect() # riconnessione al broker.


    def clientConnectionFailed(self, connector, reason):
        print("Connessione fallita, motivazione: {}".format(reason))

if __name__ == "__main__":
    reactor.connectTCP("localhost", 1883, MQTTClientFactory(clientId="test"))
    reactor.run()

