from threading import Thread, Lock
import time
import logging
from random import randrange

a = {
    'id': None,
    'value': 10
    }

def thread_function(name):
    logging.info("Thread %s   :  starting", name)
    #time.sleep(5)
    global a
    time.sleep(randrange(5))
    a['id'] = name
    tmp = a['value']
    time.sleep(randrange(5))
    a['value'] = tmp + 1
    time.sleep(randrange(5))
    logging.info("Thread %s   :  finishing (%d, %d)", name, a['id'], a['value'])

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    logging.info("Main       :  before creating thread")
    x = list()
    for i in range(10):
        x.append(Thread(target=thread_function, args=(i,)))
    #x2 = Thread(target=thread_function, args=(2,))
    logging.info("Main       :  before running thread")
    for i in range(10):
        x[i].start()
    #x1.start()
    #x2.start()
    logging.info("Main       :  wait for the thread to finish")
    for i in range(10):
        x[i].join()
    #x1.join()
    #x2.join()
    logging.info("Main       :  all done (%d, %d)", a['id'], a['value'])
