from src.utils.templates.workerprocess      import WorkerProcess
from src.brain.SteeringAngle                import SteeringAngle
from src.brain.controllerThread             import Controller
from src.brain.messageReceiver              import MessageReceiver
from src.brain.positionThread               import PositionThread
from queue import Queue


class Brain(WorkerProcess):
    def __init__(self, inPs, outPs):
        """
        Args:
            inPs[0]: from LaneDetector
            inPs[1]: from SerialHandler  ---inactiv
            inPs[2]: from gps ---inactiv
            outPs:list
        """
        super(Brain, self).__init__(inPs, outPs)
        self.angleQueue = Queue()
        #self.nucleo_data_queue = Queue()
        #self.gpsQueue = Queue()

    def _init_threads(self):
        steerAngTh = SteeringAngle(self.inPs[0], [self.angleQueue])
        self.threads.append(steerAngTh)
        
        controlTh = Controller([self.angleQueue], self.outPs[0], [])
        self.threads.append(controlTh)

        # posTh = PositionThread([self.inPs[2]], [self.gpsQueue])
        # self.threads.append(posTh)

        #messRecvTh = MessageReceiver(self.inPs[1], [self.nucleo_data_queue])
        #self.threads.append(messRecvTh)
        
    def run(self):
        super(Brain, self).run()

    def terminate(self):
        self.outPs[0].send({'action': 'BRAK', 'steerAngle': float(0)})
        super(Brain, self).terminate()
        
    def stop(self):
        self.outPs[0].send({'action': 'BRAK', 'steerAngle': float(0)})
        super(Brain, self).stop()
        
        
        
        