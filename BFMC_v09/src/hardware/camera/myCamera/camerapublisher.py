import cv2
import time
from threading import Thread
from src.utils.templates.threadwithstop import ThreadWithStop


class CameraPublisher(ThreadWithStop):
    def __init__(self, outP):
        super(CameraPublisher, self).__init__()
        self.outP = outP
        
    def run(self):
        cap = cv2.VideoCapture(0)
        while self._running:
            _, frame = cap.read()
            stamp = time.time()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.outP.send([[stamp], frame])
        cap.release()
            
            