import socket
from sys import argv
import time 

localIP     = argv[1]
localPORT   = int(argv[2])

TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
TCPServerSocket.bind((localIP, localPORT))

print('TCP Server UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
TCPServerSocket.listen()

# Accetto una nuova connessione
conn, addr = TCPServerSocket.accept()

print('Client: {}'.format(addr))

time.sleep(20)
while True:
    data = conn.recv(1024)

    if not data:
        break

    #print('{}: echo message: {}'.format(addr, data[:-1].decode('utf-8')))
    print('{}: echo message: {}'.format(addr, data))
    
    conn.sendall(data)

conn.close()
# Chiudo la connessione in essere


TCPServerSocket.close()
