import socket
from sys import argv
import re
from threading import Thread, Lock

def connection_manager_thread(id_, conn):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics
    connected = False
    print('Client: {}'.format(id_))
    regexTOPIC = r"\{\"topic\":[\ ]\"([a-zA-Z0-9]+)\"\}"
    
    while not connected:
        data = conn.recv(1024)
        if bool(re.search('^\[CONNECT\]', data.decode('utf-8'))):
            connected = True
            mutexACs.acquire()
            activeConnections[id_]['connected'] = True
            mutexACs.release()
            print('{} connected!'.format(id_))

    data = '{}\n'.format(id_)
    conn.sendall(data.encode())

    mutexACs.acquire()
    print(activeConnections)
    mutexACs.release()

    while connected:
        data = conn.recv(1024)
        if not data:
            break
        if bool(re.search('^\[DISCONNECT\]', data.decode('utf-8'))):
            connected = False

        if bool(re.search('^\[SUBSCRIBE\]', data.decode('utf-8'))):
            topic = re.findall(regexTOPIC, data.decode('utf-8'))[0]
            # logica di sottoscrizione
            mutexTOPICs.acquire()
            if not topic in topics:
                topics[topic] = set()
            
            topics[topic].add(id_)
            mutexTOPICs.release()
            #print(topics)
            # notifica utente avvenuta sottoscrizione
            response = 'Sottoscritto al topic: {}\n'.format(topic)
            conn.sendall(response.encode())

        print('{}: chat message: {}'.format(id_, data[:-1].decode('utf-8')))
    
    mutexACs.acquire()
    del activeConnections[id_]
    mutexACs.release()
    conn.close()

if __name__ == '__main__':

    localIP     = argv[1]
    localPORT   = int(argv[2])

    global activeConnections
    activeConnections = {}
    global mutexACs
    global mutexTOPICs
    mutexACs = Lock()
    mutexTOPICs = Lock()
    global topics 
    topics = dict()
    curr_id = -1;

    TCPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
    TCPServerSocket.bind((localIP, localPORT))
    
    try:

        while True:
            print('Broker UP ({},{}), waiting for connections ...'.format(localIP, localPORT))
            TCPServerSocket.listen()                    
            conn, addr = TCPServerSocket.accept()   

            mutexACs.acquire()
            activeConnections[curr_id + 1] = {
                    'address': addr,
                    'connessione': conn,
                    'connected': False,
                    'id': curr_id + 1
                    }
            curr_id += 1
            mutexACs.release()
            
            Thread(target=connection_manager_thread, args=(curr_id, conn),).start()  #

    finally:
        if TCPSeverSocket:
            TCPServerSocket.close()
