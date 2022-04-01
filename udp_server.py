import socket
from sys import argv

localIP     = '0.0.0.0'
localPORT   = int(argv[1])
bufferSize  = 1024

UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
UDPServerSocket.bind((localIP, localPORT))

print("UDP SERVER UP AND RUNNING!")

while True:
    mess, addr = UDPServerSocket.recvfrom(bufferSize)
    
    print('Messaggio ricevuto da {}'.format(addr))
    print('Messaggio: {}'.format(mess.decode('utf-8')))
 
    UDPServerSocket.sendto(str.encode('Grazie del messaggio!'), addr)
