import socket
from sys import argv
import re
from threading import Thread, Lock

def connection_manager_thread(addr, conn):
    global activeConnections
    global mutex
    connect = False
    print('Client: {}'.format(addr))
    
    while not connect:
        data = conn.recv(1024)
        if bool(re.search('^\[CONNECT\]', data.decode('utf-8'))):
            connect = True
            print('{} connected!'.format(addr))

    while connect:
        data = conn.recv(1024)
        if not data:
            break
        print('{}: chat message: {}'.format(addr, data[:-1].decode('utf-8')))
    
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
            print('Broker UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
            TCPServerSocket.listen()                    
            conn, addr = TCPServerSocket.accept()   

            mutex.acquire()
            activeConnections[addr] = conn
            mutex.release()
            
            Thread(target=connection_manager_thread, args=(addr, conn),).start()  #

    finally:
        if TCPSeverSocket:
            TCPServerSocket.close()
