from pwintools import  *

class Eleeye:
    def __init__(self, debug=False):
        self.proc = process('../eleeye/eleeye/ELEEYE.EXE') 
        self.proc.sendline(b'ucci')
        self.debug = debug
        if self.debug:
            print(self.proc.recvuntil(b'ucciok'))
    
    def recvlines(self, num_lines=None):
        for i in range(num_lines):
            line = self.proc.recvline()
            if self.debug:
                print(1)  
                print(line)
        return line

    def eleeye_move(self, in_fen=b'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1', depth=2):
        in_fen = b'position fen' + in_fen
        send_fen = self.proc.sendline(in_fen)
        if self.debug:
            print(send_fen)
        send_depth = self.proc.sendline(f'go depth {depth}'.encode())
        if self.debug:
            print(send_depth)
        recv_move = self.recvlines(num_lines=4)
        if self.debug:
            print('out:',recv_move)
        if recv_move[:8] == b'bestmove':
            if self.debug:
                print("Get Best Move!")
            move = recv_move[9:13].decode()
            if self.debug:
                print("Move of Eleeye:", move)
            return move

if __name__ == '__main__': 
    rival = Eleeye(debug=True)
    # while 1:
        # print(rival.proc.recvline())
    rival.eleeye_move(depth=5)