from xml.etree import ElementTree
from threading import Thread
from Node import Node
from time import sleep
from random import randrange
from PositionSimulator import simulator
from multiprocessing import Pipe

class PositionThread(Thread):
    def __init__(self, inPs, outQs):
        super(PositionThread, self).__init__()
        self.inP = inPs
        self.outQs = outQs
        tree = ElementTree.parse('path.xml')
        nodes = tree.getroot().findall('node')
        self.road = []
        for n in nodes:
            temp = Node(int(n.find('id').text), float(n.find('x').text), float(n.find('y').text))
            self.road.append(temp)
        for n in self.road:
            print(n.__str__())

        self.currentNode = self.road[0]
        self._running = True

    def stop(self):
        self._running = False

    def run(self):
        while self._running:
            x, y = self.inP.recv()
            tries = 0
            currentNode = self.currentNode
            while True:
                if currentNode.inRegionOfInterest(x, y):
                    print('Position: ', x, y, ' Around node: ', self.currentNode.id)
                    break
                else:
                    index = self.road.index(currentNode) + 1
                    print(index)
                    currentNode = self.road[index]


r, s = Pipe(duplex=False)
a = PositionThread(r, 2)
b = simulator(0.2, s)
a.start()
b.start()
sleep(7)
a.stop()
