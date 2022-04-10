import socket
from sys import argv
import re
from threading import Thread, Lock
import json

def decodeCommand(message):
    regexCOMMAND = r'^\[([A-Z]+)\]'
    regexJSON = r"(\{[\"a-zA-Z0-9\,\ \:\"]+\})"

    withArgs = {"SUBSCRIBE", "UNSUBSCRIBE"}    

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
    regexTOPIC = r"\{\"topic\":[\ ]\"([a-zA-Z0-9]+)\"\}"
    regexJSON = r"(\{[\"a-zA-Z0-9\,\ \:\"]+\})"
    
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
        if bool(re.search('^\[DISCONNECT\]', data.decode('utf-8'))):
            connected = False

        if bool(re.search('^\[SUBSCRIBE\]', data.decode('utf-8'))):
            stringa = re.findall(regexJSON, data.decode('utf-8'))[0]
            parametri = json.loads(stringa)
            '''
            if "topic" in parametri:
                pass
            if "topics" in parametri:
                pass
            '''
            topic = parametri["topic"]
            
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

        if bool(re.search('^\[UNSUBSCRIBE\]', data.decode('utf-8'))):
            stringa = re.findall(regexJSON, data.decode('utf-8'))[0]
            parametri = json.loads(stringa)
            topic = parametri["topic"]

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

        if bool(re.search('^\[SEND\]', data.decode('utf-8'))):
            stringa = re.findall(regexJSON, data.decode('utf-8'))[0]
            parametri = json.loads(stringa)
            topic = parametri["topic"]
            message = parametri["message"]

            # logica di invio del messaggio
            risposta = dict()
            risposta["id"] = id_
            risposta["topic"] = topic
            risposta["messaggio"] = message

            stringa = json.dumps(risposta)
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
