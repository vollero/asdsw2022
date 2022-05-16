import socket
from sys import argv
import re
from threading import Thread, Lock
import json

def decodeCommand(message, stato):
    regexCOMMAND = r"^\[([A-Z]+)\]"
    regexJSON = r"(\{[\"a-zA-Z0-9\,\ \:\"\]\[]+\})"

    withArgs = {"SUBSCRIBE", "UNSUBSCRIBE", "SEND"}    

    :wq
    command = re.findall(regexCOMMAND, message)[0]
    comando = None

    if command:
        comando = dict()
        comando['azione'] = command
        if command in withArgs and stato == "CONNESSO":
            stringa = re.findall(regexJSON, message)[0]
            parametri = json.loads(stringa)
            comando['parametri'] = parametri

    return comando

def updateState(id_, stato, comando):
    global activeConnections
    global mutexACs 

    if stato == "PRE-CONNESSIONE":
        if comando['azione'] == "CONNECT":
            newStato = "CONNESSO"
            
            mutexACs.acquire()
            activeConnections[id_]['connected'] = True
            mutexACs.release()
            print('{} connected!'.format(id_))

            return newStato

    if stato == "CONNESSO":
        if comando['azione'] == "DISCONNECT":
            newStato = "IN-USCITA"
            return newStato

    return stato

def subscribe(id_, conn, comando):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics

    if "topic" in comando['parametri']:

        topic = comando['parametri']['topic']
            
        mutexACs.acquire()
        activeConnections[id_]["topics"].add(topic)
        mutexACs.release()

        mutexTOPICs.acquire()
        if not topic in topics:
            topics[topic] = set()    
        topics[topic].add(id_)
        mutexTOPICs.release()
        print(topics)
            
        response = 'Sottoscritto al topic: {}\n'.format(topic)
        conn.sendall(response.encode())

    if "topics" in comando['parametri']:
        for topic in comando['parametri']['topics']:

            mutexACs.acquire()
            activeConnections[id_]["topics"].add(topic)
            mutexACs.release()

            mutexTOPICs.acquire()
            if not topic in topics:
                topics[topic] = set()    
            topics[topic].add(id_)
            mutexTOPICs.release()
            print(topics)
            
            response = 'Sottoscritto al topic: {}\n'.format(topic)
            conn.sendall(response.encode())

def unsubscribe(id_, conn, comando):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics

    topic = comando['parametri']['topic']

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
    
    response = 'Cancellazione della sottoscrizione al topic: {}\n'.format(topic)
    conn.sendall(response.encode())

def send(id_, conn, comando):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics

    topic = comando["parametri"]["topic"]
    message = comando["parametri"]["message"]

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

def disconnect(id_):
    global activeConnections
    global mutexACs 
    global mutexTOPICs
    global topics

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

def applyCommand(id_, conn, comando, stato):
    if (stato == "CONNESSO"):
        if comando['azione'] == "SUBSCRIBE":
            subscribe(id_, conn, comando)
            return True
        if comando['azione'] == "UNSUBSCRIBE":
            unsubscribe(id_, conn, comando)
            return True
        if comando['azione'] == "SEND":
            send(id_, conn, comando)
            return True
        if comando['azione'] == "DISCONNECT":
            disconnect(id_)
            return True
    return False

def connection_manager_thread(id_, conn):
    stato = "PRE-CONNESSIONE"               # CONNESSO, IN-USCITA
    print('Client: {}'.format(id_))

    while not (stato == "IN-USCITA"):
        data = conn.recv(1024)
        if not data:
            break
        comando = decodeCommand(data.decode('utf-8'), stato)
        applyCommand(id_, conn, comando, stato)
        stato = updateState(id_, stato, comando)
    
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
