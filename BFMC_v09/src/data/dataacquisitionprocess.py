from src.utils.templates.workerprocess import WorkerProcess
from src.data.LaneDetector import LaneDetector
from queue import Queue
from src.data.gpstracker.gpstracker import GpsTracker
from src.data.signDetector import SignDetector

class DataAcquisition(WorkerProcess):
    
    def __init__(self, inPs, outPs):
        """
         inPs[0] : from camera -> lane detection
         inPs[1] : from camera -> sign detection
         outPs[0] : from lane det -> steer angle
         outPs[1]: from gps tracker -> to path finding
         outPs[2]: from sign det -> to control
        """
        super(DataAcquisition, self).__init__(inPs, outPs)
    
    def _init_threads(self):
        """
        """
        laneDet = LaneDetector(self.inPs[0], self.outPs[0])
        self.threads.append(laneDet)

        signDet = SignDetector(self.inPs[1], self.outPs[2])
        self.threads.append(signDet)

        # gpsTracker = GpsTracker(self.outPs[1])
        # self.threads.append(gpsTracker)
        
    def run(self):
        super(DataAcquisition, self).run()