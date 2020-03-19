from threading import Thread
from src.utils.templates.threadwithstop import ThreadWithStop

class MessageReceiver(ThreadWithStop):
    def __init__(self, inP, outQs):
        """
        """
        
        super(MessageReceiver, self).__init__()
        self.inP = inP
        self.outQs = outQs
    
    def run(self):
        """
        """
        while self._running:
            data = self.inP.recv()
            #print('MessageReceiver: ' + str(data))