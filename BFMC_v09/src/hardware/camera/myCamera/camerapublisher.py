import cv2
import time
from threading import Thread
from src.utils.templates.threadwithstop import ThreadWithStop


class CameraPublisher(ThreadWithStop):
    def __init__(self, outP):
        super(CameraPublisher, self).__init__()
        self.outP = outP
        
    def run(self):
        cap = cv2.VideoCapture('/home/pi/Desktop/Exam_VER.h264')
        while self._running:
            _, frame = cap.read()
            frame = cv2.resize(frame, (640, 480))
            stamp = time.time()
            self.outP[1].send([[stamp], frame])
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            self.outP[0].send([[stamp], frame])
        cap.release()
            
            