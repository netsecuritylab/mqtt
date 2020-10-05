def _decodeValue(lengthArray):
    value = 0
    mul = 1
    for i in lengthArray[::-1]:
        value += i * mul
        mul = mul << 8
    return value

def _decodeLength(lengthArray):
    length = 0
    mul = 1
    for i in lengthArray:
        length += i & 0x7F * mul
        mul *= 0x80
        if (i & 0x80) != 0x80:
            break
    return length

def _encodeLength(length):
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

def _encodeValue(value):
    encoded = bytearray()
    encoded.append(value >> 8)
    encoded.append(value & 0xFF)
    return encoded

def _encodeString(string):
    encoded = bytearray()
    encoded.append(len(string) >> 8)
    encoded.append(len(string) & 0xFF)
    for i in string:
        encoded.append(i)
    return encoded

def _decodeString(encodedString):
    length = 256 * encodedString[0] + encodedString[1]
    return str(encodedString[2:2+length])