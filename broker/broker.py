import socket
from sys import argv
import re
from threading import Thread, Lock

def connection_manager_thread(addr, conn):
    global activeConnections
    global mutex
    global topics
    connect = False
    print('Client: {}'.format(addr))
    
    while not connect:
        data = conn.recv(1024)
        if bool(re.search('^\[CONNECT\]', data.decode('utf-8'))):
            connect = True
            mutex.acquire()
            activeConnections[addr]['connected'] = True
            mutex.release()
            print('{} connected!'.format(addr))

    while connect:
        data = conn.recv(1024)
        if not data:
            break
        if bool(re.search('^\[DISCONNECT\]', data.decode('utf-8'))):
            connect = False

        if bool(re.search('^\[SUBSCRIBE\]', data.decode('utf-8'))):
            # {'topic': '<nome_topic>'}

            pass

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
    global topics = {}
    curr_id = -1;

    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPORT))
    
    try:

        while True:
            print('Broker UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
            TCPServerSocket.listen()                    
            conn, addr = TCPServerSocket.accept()   

            mutex.acquire()
            activeConnections[addr] = {
                    'connessione': conn,
                    'connected': False,
                    'id': curr_id + 1
                    }
            curr_id += 1
            mutex.release()
            
            Thread(target=connection_manager_thread, args=(addr, conn),).start()  #

    finally:
        if TCPSeverSocket:
            TCPServerSocket.close()
