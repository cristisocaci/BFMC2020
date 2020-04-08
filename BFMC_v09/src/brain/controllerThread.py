from src.utils.templates.threadwithstop import ThreadWithStop
import logging
from time import sleep


class Controller(ThreadWithStop):
    def __init__(self, inQs, outP, inPs):
        """
        Args:
            inQs[0]: input from steering angle thread ( gives a steering angle )
            outP: sends commands to serial handler
            inPs[0]: from sign detection

        """
        super(Controller, self).__init__()
        self.inQs = inQs
        self.outP = outP
        self.inPs = inPs

        logging.basicConfig(filename='src/brain/control.log', filemode = 'w', format='%(message)s')
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)

        self.allowedOffset = 50  # needs more testing
        self.allowedDistanceFromLine = 250  # needs more testing
        self.allowedMisreadings = 10  # needs more testing
        self.misreadings = 0

        sleep(2)
        self.startSpeed = 0.17

        self.outP.send({'action': 'MCTL', 'speed': self.startSpeed, 'steerAngle' : 0.0})

        self.forwardSpeed = 0.15
        self.rightTurnSpeed = 0.16
        self.leftTurnSpeed = 0.16
        self.backwardSpeed = -0.15
        self.safeSpeed = 0.15

        sleep(1)
        self.outP.send({'action': 'MCTL', 'speed': self.forwardSpeed, 'steerAngle': 0.0})

    def make_command(self, steer_angle=0.0, speed=0.17, stop=False, debugInfo = 'No debug info: '):
        if stop:
            data = {'action': 'BRAK', 'steerAngle': float(0)}
        else:
            data = {'action': 'MCTL', 'speed': float(speed), 'steerAngle': float(steer_angle)}
        self.logger.debug(debugInfo + str(data))
        return data

    # from here are basic moving commands
    def forward(self, steer, speed=0.18, debugInfo='Forward'):
        debugInfo += ' - Forward: '
        max_steer = 0.5
        if steer > max_steer:
            steer = max_steer
        elif steer < -max_steer:
            steer = -max_steer
        self.outP.send(self.make_command(steer, speed, debugInfo=debugInfo))

    def backward(self, speed=-0.18, steer=0.0, time=0.5, debugInfo='Backward'):
        debugInfo += ' - Backward: '
        self.outP.send(self.make_command(stop=True, debugInfo=debugInfo))
        self.outP.send(self.make_command(steer_angle=steer, speed=speed, debugInfo=debugInfo))
        sleep(time)
        self.outP.send(self.make_command(stop=True, debugInfo=debugInfo))

    def stop(self, time=2.0, debugInfo='Stop'):
        debugInfo += ' - Stop: '
        self.outP.send(self.make_command(stop=True, debugInfo=debugInfo))
        sleep(time)

    def left_turn(self, steer_angle=0.0, speed=0.18,
                  start_point=(0,0), end_point=(0,0), radius=1.035, arc=False, debugInfo='TurnLeft'):
        """ If arc is true the car will take the angles based on the end points of the curve and the radius """
        debugInfo += ' - TurnLeft: '
        if arc:     # hard code something
            pass  # cannot be implemented without the imu sensor
        else:
            self.outP.send(self.make_command(steer_angle, speed, debugInfo=debugInfo))

    def right_turn(self, steer_angle=0.0, speed=0.17,
                   start_point=(0,0), end_point=(0,0), radius=0.665, arc=False, debugInfo='TurnRight'):
        """ If arc is true the car will take the angles based on the end points of the curve and the radius """
        debugInfo += ' - TurnRight: '
        if arc:     # hard code something
            pass # cannot be implemented without the imu sensor
        else:
            self.outP.send(self.make_command(steer_angle, speed, debugInfo=debugInfo))

    # from here are maneuvers
    def stop_maneuver(self, waiting_time):
        self.stop(waiting_time)
        self.forward(speed=self.startSpeed, steer=0, debugInfo='Stop Maneuver')

    def pedestrian_crossing_maneuver(self, ang):
        self.forward(steer=ang, speed=self.safeSpeed, debugInfo='Pedestrian Crossing Maneuver')

    def parking_maneuver(self):
        self.forward(0.0, self.safeSpeed, debugInfo='Parking Maneuver')
        sleep(1)
        self.stop(0.1, debugInfo='Parking Maneuver')
        self.backward(speed=self.backwardSpeed, steer=19.5, time=0.5, debugInfo='Parking Maneuver')
        self.stop(0.1, debugInfo='Parking Maneuver')
        self.backward(speed=self.backwardSpeed, steer=-19.5, time=0.5, debugInfo='Parking Maneuver')
        self.stop(1, debugInfo='Parking Maneuver')
        # TODO: implement the maneuver to get out of the parking spot

    def normal_driving(self, lines, dist_from_right, dist_from_left, steer_ang):
        if lines == 2 and dist_from_right > self.allowedDistanceFromLine \
                and dist_from_left > self.allowedDistanceFromLine:  # moving forward case (with confidence :D )
            offset = abs(dist_from_left - dist_from_right)
            if offset > self.allowedOffset:
                self.forward(steer_ang, speed=self.forwardSpeed, debugInfo='Normal Driving')
            self.misreadings = 0

        elif lines == 2:  # moving forward case (without confidence :D )
            if steer_ang != 0:
                angle = steer_ang / abs(steer_ang) * 5
            else:
                angle = 0
            self.outP.send(self.make_command(steer_angle=angle, speed=self.safeSpeed, debugInfo='Normal Driving'))
            self.misreadings = 0

        elif lines == 10:  # turn left case
            if dist_from_right < self.allowedDistanceFromLine:  # this means that its going outside the lines
                self.left_turn(steer_ang, speed=self.leftTurnSpeed, debugInfo='Normal Driving')
                pass  # needs an avoidance strategy
            else:
                self.left_turn(steer_ang, speed=self.leftTurnSpeed, debugInfo='Normal Driving')
            self.misreadings = 0

        elif lines == 11:  # turn right case
            if dist_from_left < self.allowedDistanceFromLine:  # this means that its going outside the lines
                self.right_turn(steer_ang, speed=self.rightTurnSpeed, debugInfo='Normal Driving')
                pass  # needs an avoidance strategy
            else:
                self.right_turn(steer_ang, speed=self.rightTurnSpeed, debugInfo='Normal Driving')
                self.misreadings = 0

        elif lines == 0:  # no lines detected
            """ 
            -count how many times this happens and if it happens more than a threshold
             value move backwards in order to go back between the lines
            -count in order to avoid some misreadings
            -in the future -> implement intersection crossing 
             """
            #self.misreadings += 1
            #if self.misreadings == self.allowedMisreadings:
             #   self.backward(speed=self.backwardSpeed, time=1, debugInfo='Normal Driving')
              #  self.misreadings = 0
            self.forward(0.0, self.safeSpeed, debugInfo='Normal Driving')

    def intersection_crossing(self, direction):
        self.stop(1, debugInfo='Intersection Crossing')
        self.forward(0.0, self.startSpeed, debugInfo='Intersection Crossing')
        sleep(0.2)
        if direction == 'left':
            self.left_turn(steer_angle=-15.5, speed=self.leftTurnSpeed, debugInfo='Intersection Crossing')
            sleep(4.5)
        elif direction == 'right':
            self.right_turn(steer_angle=20.0, speed=self.rightTurnSpeed, debugInfo='Intersection Crossing')
            sleep(3)
        elif direction == 'straight':
            self.forward(0, self.safeSpeed, debugInfo='Intersection Crossing')
            sleep(3)

    def run(self):
        while self._running:

            steer_ang, lines, dist_from_right, dist_from_left, horizontal_line = self.inQs[0].get()
            self.logger.debug('Control: steering angle: ' + str(steer_ang))
            self.logger.debug('Control: lines: ' + str(lines) + ', dist right: ' + str(dist_from_right) +
                              ', dist left: ' + str(dist_from_left))
            sign = 0  # = self.inPs[0].recv()
            # stop = 1; prioritate = 2; parcare = 3; trecere = 4; nimic = 0
            
            if horizontal_line:  # detected the horizontal line before an intersection => intersection crossing maneuver
                while horizontal_line:
                    steer_ang, lines, dist_from_right, dist_from_left, horizontal_line = self.inQs[0].get()
                    self.normal_driving(lines, dist_from_right, dist_from_left, steer_ang)
                    
                # TODO: add path planning to know where to go in intersection
                # TODO: add check mechanism to be sure that the line detected is indeed the one from the intersection
                self.intersection_crossing("left")
                
            if sign == 0:    # it goes normal
                self.normal_driving(lines, dist_from_right, dist_from_left, steer_ang)
            elif sign == 1:     # stops at the sign
                self.stop_maneuver(2)

            elif sign == 2:     # parking maneuver
                self.parking_maneuver()

            elif sign == 3:     # slow down and search for pedestrian -- latter not implemented yet
                self.pedestrian_crossing_maneuver(steer_ang)
    
                
                


