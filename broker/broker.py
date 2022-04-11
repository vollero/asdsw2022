import socket
from sys import argv
import re
from threading import Thread, Lock
import json

def decodeCommand(message):
    regexCOMMAND = r'^\[([A-Z]+)\]'
    regexJSON = r"(\{[\"a-zA-Z0-9\,\ \:\"]+\})"

    withArgs = {"SUBSCRIBE", "UNSUBSCRIBE", "SEND"}    

    command = re.findall(regexCOMMAND, message)[0]
    comando = None

    if command:
        comando = dict()
        comando['azione'] = command
        if command in withArgs:
            stringa = re.findall(regexJSON, message)[0]
            parametri = json.loads(stringa)
            comando['parametri'] = parametri

    return comando

def connection_manager_thread(id_, conn):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics
    connected = False
    print('Client: {}'.format(id_))
    
    while not connected:
        data = conn.recv(1024)
        comando = decodeCommand(data.decode('utf-8'))
        if comando['azione'] == "CONNECT":
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

        comando = decodeCommand(data.decode('utf-8'))

        if comando['azione'] == "DISCONNECT":
            connected = False

        if comando['azione'] == "SUBSCRIBE":
            topic = comando['parametri']['topic']
            
            # logica di sottoscrizione
            mutexACs.acquire()
            activeConnections[id_]["topics"].add(topic)
            mutexACs.release()

            mutexTOPICs.acquire()
            if not topic in topics:
                topics[topic] = set()    
            topics[topic].add(id_)
            mutexTOPICs.release()
            print(topics)
            
            # notifica utente avvenuta sottoscrizione
            response = 'Sottoscritto al topic: {}\n'.format(topic)
            conn.sendall(response.encode())

        if comando['azione'] == "UNSUBSCRIBE":
            topic = comando['parametri']['topic']

            # logica di sottoscrizione
            mutexACs.acquire()
            activeConnections[id_]["topics"].remove(topic)
            mutexACs.release()

            mutexTOPICs.acquire()
            if topic in topics:
                if id_ in topics[topic]:
                    topics[topic].remove(id_)
                if len(topics[topic]) == 0:
                    del topics[topic]
            mutexTOPICs.release()
            print(topics)
            # notifica utente avvenuta sottoscrizione
            response = 'Cancellazione della sottoscrizione al topic: {}\n'.format(topic)
            conn.sendall(response.encode())

        if comando['azione'] == "SEND":
            topic = comando["parametri"]["topic"]
            message = comando["parametri"]["message"]

            # logica di invio del messaggio
            risposta = dict()
            risposta["id"] = id_
            risposta["topic"] = topic
            risposta["messaggio"] = message

            stringa = json.dumps(risposta) + '\n'
            print(stringa)

            mutexACs.acquire()
            mutexTOPICs.acquire()
            subscribers = topics[topic]
            for subID in subscribers:
                recv_conn = activeConnections[subID]["connessione"]
                recv_conn.sendall(stringa.encode())
            mutexTOPICs.release()
            mutexACs.release()

        print('{}: chat message: {}'.format(id_, data[:-1].decode('utf-8')))
    
    mutexACs.acquire()
    curr_topics = activeConnections[id_]["topics"]    
    mutexACs.release()

    mutexTOPICs.acquire()
    for topic in curr_topics:
        topics[topic].remove(id_)
        if len(topics[topic]) == 0:
            del topics[topic]
    mutexTOPICs.release()

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
                    'id': curr_id + 1,
                    'topics': set()
                    }
            curr_id += 1
            mutexACs.release()
            
            Thread(target=connection_manager_thread, args=(curr_id, conn),).start()  #

    finally:
        if TCPSeverSocket:
            TCPServerSocket.close()
