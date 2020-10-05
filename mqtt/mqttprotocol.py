from twisted.internet.protocol import Protocol

class MQTTProtocol(Protocol):

    """buffer = bytearray()
    availablePackets = {
            0x00: "null",
            0x01: "connect",
            0x02: "connack",
            0x03: "publish",
            0x04: "puback",
            0x05: "pubrec",
            0x06: "pubrel",
            0x07: "pubcomp",
            0x08: "subscribe",
            0x09: "suback",
            0x0A: "unsubscribe",
            0x0B: "unsuback",
            0x0C: "pingreq",
            0x0D: "pingresp",
            0x0E: "disconnect"
        }"""

    def __init__(self):
        self.buffer = bytearray()
        self.availablePackets = {
            0x00: "null",
            0x01: "connect",
            0x02: "connack",
            0x03: "publish",
            0x04: "puback",
            0x05: "pubrec",
            0x06: "pubrel",
            0x07: "pubcomp",
            0x08: "subscribe",
            0x09: "suback",
            0x0A: "unsubscribe",
            0x0B: "unsuback",
            0x0C: "pingreq",
            0x0D: "pingresp",
            0x0E: "disconnect"
        }


    def connectionMade(self):
        print("[PROTOCOL] CONNESSIONE EFFETTUATA")

    def connectionLost(self, reason):
        pass

    def dataReceived(self, data):
        
        self._packetQueue(data)

    def _packetQueue(self, data):
        self.buffer.extend(data)
        length = None
        while len(self.buffer):
            if length is None:
                # si ha un pacchetto da processare

                if len(self.buffer) < 2: # non ci sono abbastanza dati per inizializzare un nuovo pacchetto
                    break

                newLength = 1

                while newLength < len(self.buffer):
                    if not self.buffer[newLength] & 0x80:
                        break
                    newLength += 1

                if newLength < len(self.buffer) and self.buffer[newLength] & 0x80:
                    return

                length = self._decodeLength(self.buffer[1:])

                if len(self.buffer) >= length:
                    chunk = self.buffer[:length + newLength + 1]
                    self._workPacket(chunk)
                    self.buffer = self.buffer[length + newLength + 1:]
                    length = None
                else:
                    break
        
    def _workPacket(self, packet):
        try:
            packetType = self.availablePackets[(packet[0] & 0xF0) >> 4]
            print("[PROTOCOL] RICEVO => " + upper(packetType))
            duplicate = (packet[0] & 0x08) == 0x08
            packetQoS = (packet[0] & 0x06) >> 1
            retain = (packet[0] & 0x01) == 0x01
        except:
            print("Tipologia pacchetto non riconosciuta.")
            return

        newLength = 1
        while packet[newLength] & 0x80:
            newLength += 1

        packet = packet[newLength+1:]
        packetHandler = getattr(self, "{}_event".format(packetType), None)
        if packetHandler:
            packetHandler(packet, packetQoS, duplicate, retain)
        else:
            print("Non posso gestire questo pacchetto.")
            return

    def connack_event(self, packet, qos, dup, retain):
        self.connackReceived(packet[0])


    def connect_event(self, packet, qos, dup, retain):
        packet = packet[len("06MQisdp3")]

        willRetain = packet[0] & 0x20 == 0x20
        willQoS = packet[0] & 0x18 >> 3
        willFlag = packet[0] & 0x04 == 0x04
        cleanStart = packet[0] & 0x02 == 0x02
        
        packet = packet[1:]
        keepalive = self._decodeValue(packet[:2])

        packet = packet[2:]

        clientId = self._decodeString(packet)
        packet = packet[len(clientId) + 2:]

        willTopic = None
        willMessage = None
        if willFlag:
            willTopic = self._decodeString(packet)
            packet = packet[len(willTopic) + 2:]
            willMessage = packet

        self.connectReceived(clientId, keepalive, willTopic, willMessage, willQoS, willRetain, cleanStart)

    def connect(self, clientId, keepalive=60, willTopic=None, willMessage=None, willQoS=0, willRetain=False, cleanStart=True):
        
        header = bytearray()
        varHeader = bytearray()
        payload = bytearray()
        
        varHeader.extend(self._encodeString(b"MQTT")) # nome del protocollo
        varHeader.append(4) # versione del protocollo

        if willMessage is None or willTopic is None:
            varHeader.append(0 << 2 | cleanStart << 1) # byte per il cleanSession
        else:
            varHeader.append(willRetain << 5 | willQoS << 3 | 1 << 2 | cleanStart << 1)

        varHeader.extend(self._encodeValue(keepalive//1000)) # byte per il keepalive

        payload.extend(self._encodeString(bytes(clientId, "utf-8"))) # clientId in bytes, utf-8.

        if willMessage is not None and willTopic is not None:
            payload.extend(self._encodeString(bytes(willTopic, "utf-8"))) # topic
            payload.extend(self._encodeString(bytes(willMessage, "utf-8"))) # message

        header.append(0x01 << 4)
        header.extend(self._encodeLength(len(varHeader) + len(payload)))

        self.transport.write(header)
        self.transport.write(varHeader)
        self.transport.write(payload)

    def connack(self, status):
        header = bytearray()
        payload = bytearray()

        header.append(0x02 << 4)
        payload.append(status)

        header.extend(self._encodeLength(len(payload)))
        self.transport.write(header)
        self.transport.write(payload)


    def connackReceived(self, status):
        pass

    def _decodeString(self, encodedString):
        length = 256 * encodedString[0] + encodedString[1]
        return str(encodedString[2:2+length])

    def connectReceived(self, clientId, keepalive, willTopic, willMessage, willQoS, willRetain, cleanStart):
        pass

    def _decodeValue(self, lengthArray):
        value = 0
        mul = 1
        for i in valueArray[::-1]:
            value += i * mul
            mul = mul << 8
        return value

    def _decodeLength(self, lengthArray):
        length = 0
        mul = 1
        for i in lengthArray:
            length += i & 0x7F * mul
            mul *= 0x80
            if (i & 0x80) != 0x80:
                break
        return length

    def _encodeLength(self, length):
        encoded = bytearray()
        while True:
            digit = length % 128
            length //=128

            if length > 0:
                digit |= 128

            encoded.append(digit)
            if length <= 0:
                break
        return encoded

    def _encodeValue(self, value):
        encoded = bytearray()
        encoded.append(value >> 8)
        encoded.append(value & 0xFF)
        return encoded

    def _encodeString(self, string):
        encoded = bytearray()
        encoded.append(len(string) >> 8)
        encoded.append(len(string) & 0xFF)
        for i in string:
            encoded.append(i)
        return encoded


