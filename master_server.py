import socket
from sys import argv
import re
from threading import Thread, Lock

def sendToAll(addr, data):
    global activeConnections
    global mutex

    mutex.acquire()
    for eaddr, econn in activeConnections.items():
        if not eaddr == addr:
            print('{}: {}'.format(eaddr, data))
            econn.sendall(data)
    mutex.release()

def connection_manager_thread(addr, conn):
    global activeConnections
    global mutex
    print('Client: {}'.format(addr))
    while True:
        data = conn.recv(1024)
        if not data:
            break
        
        print('{}: chat message: {}'.format(addr, data[:-1].decode('utf-8')))

        dataToSend = '{}: {}'.format(addr, data.decode('utf-8'))
        sendToAll(addr, dataToSend.encode())

    mutex.acquire()
    del activeConnections[addr]
    mutex.release()
    conn.close()

if __name__ == '__main__':

    localIP     = argv[1]
    localPORT   = int(argv[2])

    global activeConnections
    activeConnections = {}
    global mutex
    mutex = Lock()

    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPORT))
    
    try:

        while True:
            print('Master Server UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
            TCPServerSocket.listen()                    #
            conn, addr = TCPServerSocket.accept()       #

            mutex.acquire()
            activeConnections[addr] = conn
            mutex.release()
            
            Thread(target=connection_manager_thread, args=(addr, conn),).start()  #

    finally:
        if TCPSeverSocket:
            TCPServerSocket.close()
