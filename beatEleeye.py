from pwintools import  *

class Eleeye:
    def __init__(self):
        self.proc = process('../eleeye/eleeye/ELEEYE.EXE') 
        self.proc.sendline(b'ucci')
        print(self.proc.recvuntil(b'ucciok'))
        print(1)
    
    def recvlines(self, num_lines=None):
        for i in range(num_lines):
            line = self.proc.recvline()  
            print(line)
        return line

    def eleeye_move(self, in_fen=b'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR w - - 0 1', depth=2):
        in_fen = b'position fen' + in_fen
        print(self.proc.sendline(in_fen))
        print(self.proc.sendline(f'go depth {depth}'.encode()))
        out = self.recvlines(num_lines=4)
        print('out',out)
        if out[:8] == b'bestmove':
            print(2)
            move = out[9:13].decode()
            print(move)
            return move

if __name__ == '__main__': 
    rival = Eleeye()
    # while 1:
        # print(rival.proc.recvline())
    rival.eleeye_move()