import sys

from twisted.internet import reactor, task
from twisted.internet.defer import inlineCallbacks, DeferredList
from twisted.application.internet import ClientService, backoffPolicy
from twisted.internet.endpoints import clientFromString
from twisted.logger import (Logger, LogLevel, globalLogBeginner, textFileLogObserver, FilteringLogObserver, LogLevelFilterPredicate)

from mqtt.client.factory import MQTTFactory
import pyradamsa
import random

endpoint = "tcp:localhost:1883"
logLevelFilterPredicate = LogLevelFilterPredicate(defaultLogLevel=LogLevel.debug)
radamsa = pyradamsa.Radamsa()

def startLogging(console=True, filepath=None):
    
    observers = []

    if console:
        observers.append(FilteringLogObserver(observer=textFileLogObserver(sys.stdout), predicates=[logLevelFilterPredicate]))
    
    if filepath is not None and filepath != "":
        observers.append(FilteringLogObserver(observer=textFileLogObserver(open(filepath, 'a')), predicates=[logLevelFilterPredicate]))
    
    globalLogBeginner.beginLoggingTo(observers)


def setLogLevel(namespace=None, levelStr='info'):
    level = LogLevel.levelWithName(levelStr)
    logLevelFilterPredicate.setLogLevelForNamespace(namespace=namespace, level=level)


class MQTTService(ClientService):

    def __init__(self, endpoint, factory, id):
        self.endpoint = endpoint
        ClientService.__init__(self, endpoint, factory, retryPolicy=backoffPolicy())
        self.id = id


    def startService(self):
        log.info("Publisher MQTT inizializzato")

        self.whenConnected().addCallback(self.connectToBroker)
        ClientService.startService(self)

    
    @inlineCallbacks
    def connectToBroker(self, protocol):
        self.protocol = protocol
        self.protocol.onDisconnection = self.onDisconnection
        self.protocol.setWindowSize(1)
        self.task = task.LoopingCall(self.publish)
        self.task.start(10)

        try:
            yield self.protocol.connect("myClientId" + str(self.id), keepalive=0)
        except Exception as e:
            log.error(("Connecting to {} raised {}".format(self.endpoint, str(e))))
        else:
            log.info("Connesso al broker {broker}", broker=self.endpoint)


    def onDisconnection(self, reason):
        log.debug("Disconnesso, motivazione: {r}", r=reason)
        self.whenConnected().addCallback(self.connectToBroker)


    def publish(self):

        def _logFailure(failure):
            log.debug("errore: {f}", f=failure.getErrorMessage())

        def _logAll(*args):
            log.debug("publishing completo: {args}", args=args)

        log.debug("Publishing")

        fuzzed_data = radamsa.fuzz(bytes("hello", "utf-8"))
        #print(fuzzed_data)

        a = ""

        """for i in range(0, 0xF4240): # 1mb
            a += "a"
        """

        """for i in range(0, 0x989680): # 10mb
            a += "a"
        """
        

        for i in range(0, 10): # 100mb
            a += "a"
        

        d1 = self.protocol.publish(topic="/valid/\\xff\\xfe#\\x00/", qos=0, message=a)
        d1.addErrback(_logFailure)

        dlist = DeferredList([d1], consumeErrors=True)
        dlist.addCallback(_logAll)

        return dlist


if __name__ == "__main__":
    import sys
    #import generate_tests

    #tests = generate_tests.GenerateTests("./test_case/connect/")
    #buildedTests = tests.buildTest(testNumber=5, writeToFiles=False)
    #print(buildedTests)
    log = Logger()
    startLogging()

    setLogLevel(namespace="mqtt", levelStr="debug")
    setLogLevel(namespace="__main__", levelStr= "debug")

    factory = MQTTFactory(profile=MQTTFactory.PUBLISHER)
    myend = clientFromString(reactor, endpoint)
    services = []
    n = 100

    serv = MQTTService(myend, factory, 1)
    serv.startService()
    """for i in range(0, 10):
        serv = MQTTService(myend, factory, i)
        services.append(serv)

    for i in range(0, 10):
        services[i].startService()"""
    reactor.run()
