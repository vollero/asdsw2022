from cmd import Cmd
import socket
import json

class myPrompt(Cmd):
    prompt = '>'
    intro  = 'Ciao, benvenuto nel mio prompt:' 
   
    def __init__(self):
        super().__init__()
        self.socket = None
        self.is_connect = False

    def do_ciao(self, inp):
        print('Ciao a te')

    def do_exit(self, inp):
        print('Ciao e alla prossima!')
        self.close()
        return True
    
    def do_connect(self, inp):
        if not self.is_connect:
            args = inp.split(' ')
            address = args[0]
            port    = int(args[1])
            self.socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
            self.socket.connect((address, port))
            self.is_connect = True
            print(self.socket)

    def do_disconnect(self, inp):
        if self.is_connect:
            self.socket.close()
            self.is_connect = False

    def do_sendMessage(self, inp):
        if self.is_connect:
            messaggio = inp + '\n'
            self.socket.sendall(messaggio.encode('UTF-8'))

    # Chiudere tutte le risorse potenzialmente attive
    def close(self):
        if self.is_connect:
            self.socket.close()
        pass

if __name__ == '__main__':
    prompt = myPrompt()
    prompt.cmdloop()
