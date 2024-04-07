import sys
import time
import threading
import random
import signal
from functools import partial


def handler(signum, frame, state, threads):
    state.set()
    for philozopher in threads:
        philozopher.join()
    exit()

class Chopstic:
    def __init__(self, is_rised):
        self.is_rised = is_rised

    def can_pickup(self):
        return not self.is_rised
    
    def pickup(self):
        if not self.is_rised:
            self.is_rised = 1
            return True
        return False

    def put_down(self):
        if self.is_rised:
            self.is_rised = 0
            return True
        return False

class Philozopher:
    # right and left is from the point of view of the table
    def __init__(self, number,left = False,right = False, is_eating=0):
        self.number = number
        self.is_eating = is_eating
        self.left = left
        self.right = right

    def eat_no_opt(self, chopstics, finnished):
        while not finnished.is_set():
            time.sleep(random.randint(0, THINK_TIME_MAX_ms)/1000)

            if not self.right:
                self.right = chopstics[self.number].pickup()
            if not self.left:
                self.left = chopstics[self.number-1].pickup()
            if self.right and self.left:
                self.is_eating = 1
                time.sleep(random.randint(0, EAT_TIME_MAX_ms)/1000)
                self.is_eating = 0
                chopstics[self.number].put_down()
                chopstics[self.number-1].put_down()
                self.left = False
                self.right = False

    def eat_opt_1(self, chopstics, finnished):
        while not finnished.is_set():
            time.sleep(random.randint(0, THINK_TIME_MAX_ms)/1000)
            if chopstics[self.number].can_pickup() and chopstics[self.number-1].can_pickup():
                self.right = chopstics[self.number].pickup()
                self.left = chopstics[self.number-1].pickup()
                if self.right and self.left:
                    self.is_eating = 1
                    time.sleep(random.randint(0, EAT_TIME_MAX_ms)/1000)
                    self.is_eating = 0
                    chopstics[self.number].put_down()
                    chopstics[self.number-1].put_down()
                    self.left = False
                    self.right = False        

    def eat_opt_2(self, chopstics, finnished):
        while not finnished.is_set():
            time.sleep(random.randint(0, THINK_TIME_MAX_ms)/1000)
            if not self.number%2:
                self.right = chopstics[self.number].pickup()
                if self.right:
                    self.left = chopstics[self.number-1].pickup()
            else:                                
                self.left = chopstics[self.number-1].pickup()
                if self.left:
                    self.right = chopstics[self.number].pickup()
            if self.right and self.left:
                self.is_eating = 1
                time.sleep(random.randint(0, EAT_TIME_MAX_ms)/1000)
                self.is_eating = 0
                chopstics[self.number].put_down()
                chopstics[self.number-1].put_down()
                self.left = False
                self.right = False    
                


def simulation(n, typ):
    chopstics = []    
    for _ in range(n):
        chopstics.append(Chopstic(0))

    philozophers = []
    for i in range(n):
        philozophers.append(Philozopher(i))  

    finnished = threading.Event()
    philozophers_threads = []
    if typ == 0:
        for philoz in philozophers:
            philozophers_threads.append(threading.Thread(target=philoz.eat_no_opt, args=(chopstics, finnished,)))

    elif typ == 1:
        for philoz in philozophers:
            philozophers_threads.append(threading.Thread(target=philoz.eat_opt_1, args=(chopstics, finnished,)))

    else:
        for philoz in philozophers:
            philozophers_threads.append(threading.Thread(target=philoz.eat_opt_2, args=(chopstics, finnished,)))
    
    
    for philoz in philozophers_threads:
        philoz.start()

    partial_handler = partial(handler, state=finnished, threads=philozophers_threads)
    signal.signal(signal.SIGINT, partial_handler)

    while True:
        time.sleep(REFRESH_RATE_S)
        state = ''
        for i in range(n):
            state += str(philozophers[i].is_eating)
            state += '+' if chopstics[i].is_rised else '-'

        print(state)

        is_jammed = 1
        for philozopher in philozophers:
            if philozopher.is_eating:
                is_jammed = 0
        for stick in chopstics:
            if not stick.is_rised:
                is_jammed = 0
        if is_jammed:
            finnished.set()
            for philozopher in philozophers_threads:
                philozopher.join()
            print('JAMMED!')
            exit()


if __name__ == '__main__':
    
    REFRESH_RATE_S = 0.5
    THINK_TIME_MAX_ms = 1000
    EAT_TIME_MAX_ms = 1000

    if len(sys.argv) != 3:
        print('usage: py filozofowie.py <typ> <n>')
        exit()

    n = int(sys.argv[2])
    typ = int(sys.argv[1])
    
    if n < 2 or n > 10:
        print('inforrect number of philozophers, can be 2-10')
        exit()

    if typ not in [0, 1, 2]:
        print('typ can be either 1 or 2 or 0')
        exit()

    simulation(n, typ)