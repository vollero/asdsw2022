from threading import Thread, Lock
import time
import logging
from random import randrange

mutex = Lock()
sharedBuffer = ''

def thread_writer(name):
    global sharedBuffer
    global mutex
    logging.info("WThread %s  :  starting", name)
    time.sleep(randrange(1,10))

    mutex.acquire()
    
    sharedBuffer = r'WThred {} ha iniziato a scrivere nel buffer'.format(name)
    time.sleep(randrange(1,10))
    sharedBuffer = r'{} ed ha terminato di scrivere'.format(sharedBuffer)
    
    mutex.release()

    logging.info("WThread %s  :  finishing", name)

def thread_reader(name):
    global sharedBuffer
    global mutex
    logging.info("RThread %s  :  starting", name)
    time.sleep(randrange(2,20))

    mutex.acquire()

    logging.info("RThread %s  :  MESSAGE: %s", name, sharedBuffer)

    mutex.release()

    logging.info("WThread %s  :  finishing", name)

if __name__ == "__main__":
    numeroThread = 20
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main       :  before creating threads")
    
    listaThreadWriter = []
    listaThreadReader = []

    for nomeThread in range(numeroThread):
        listaThreadWriter.append(Thread(target=thread_writer, args=(nomeThread,)))
    for nomeThread in range(numeroThread):
        listaThreadReader.append(Thread(target=thread_reader, args=(nomeThread,)))
    
    logging.info("Main       :  before running threads")

    for eThread in listaThreadWriter:
        eThread.start()
    for eThread in listaThreadReader:
        eThread.start()
    
    logging.info("Main       :  wait for the threads to finish")

    for eThread in listaThreadWriter:
        eThread.join()
    for eThread in listaThreadReader:
        eThread.join()

    logging.info("Main       :  all done")
