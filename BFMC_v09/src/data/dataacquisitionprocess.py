from src.utils.templates.workerprocess import WorkerProcess
from src.data.LaneDetector import LaneDetector
from queue import Queue
from src.data.gpstracker.gpstracker import GpsTracker

class DataAcquisition(WorkerProcess):
    
    def __init__(self, inPs, outPs):
        """
         inPs[0] : from camera
         outPs[0] : to steer angle
         outPs[1]: to path finding
        """
        super(DataAcquisition, self).__init__(inPs, outPs)
    
    def _init_threads(self):
        """
        """
        laneDet = LaneDetector(self.inPs[0], self.outPs[0])
        self.threads.append(laneDet)
        
        # gpsTracker = GpsTracker(self.outPs[1])
        # self.threads.append(gpsTracker)
        
    def run(self):
        super(DataAcquisition, self).run()