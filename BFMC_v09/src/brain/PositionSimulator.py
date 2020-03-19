from time import sleep
from threading import Thread

class simulator(Thread):

    def __init__(self, speed, outP):
        super(simulator, self).__init__()
        self.speed = speed
        self.outP = outP
        self.x = 0.35
        self.y = 5.45

    def run(self):
        count = 0
        while True:
            self.outP.send((self.x,self.y))
            self.x += self.speed
            sleep(1)
            count += 1
            if count == 15:
                break

