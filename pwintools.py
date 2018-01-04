from subprocess import Popen, PIPE, call
import threading, sys
 
'''
this is a self defined class as a simple pwntool replacement
when there is not intalled pwntool 
'''
 
class process:
    def __init__(self, cmd):
        self.pipe = Popen(cmd, stdin = PIPE, stdout = PIPE, shell = True)
 
    def sendline(self, delims): 
        self.pipe.stdin.write(delims + b'\n')
        self.pipe.stdin.flush()
        return delims + b'\n'
 
    def send(self, delims):
        self.pipe.stdin.write(delims)
        self.pipe.stdin.flush()
     
    def recv(self, count):
        return self.pipe.stdout.read(count)
 
    def recvline(self):
        return self.pipe.stdout.readline()
 
    def recvuntil(self, delims):
        buf = b''
        while delims not in buf:            
            buf += self.recv(1)
        return buf
 
    def recvline_startswith(self, delims):
        buf = ''
        while '\n' + delims not in buf:
            buf += self.read(1)
         
        while True:
            tmp = self.read(1)
            buf += tmp
            if buf == '\n':
                break
        return buf
 
    def interactive(self):
        print('Switching to interative mode')
        go = threading.Event()
        def recv_thread():
            while not go.isSet():
                try:
                    cur = self.recv(1)
                    sys.stdout.write(cur)
                    sys.stdout.flush()
                except EOFError:
                    print('Got EOF while reading in interactive')
                    break
        t = threading.Thread(target = recv_thread)
        t.setDaemon(True)
        t.start()
        while self.pipe:
            print('$ '),
            while True:
                data = sys.stdin.read(1)
                self.send(data)
                if data == '\n':
                    break 