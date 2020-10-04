import socket

host = 'localhost'
port = 1883
buffer_size = 1024
message = b"Hi"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))
s.send(message)
data = s.recv(buffer_size)
s.close()

print(data)