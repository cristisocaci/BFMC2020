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
        self.startSpeed = 0.2

        self.outP.send({'action': 'MCTL', 'speed': self.startSpeed, 'steerAngle' : 0.0})

        self.forwardSpeed = 0.18
        self.rightTurnSpeed = 0.16
        self.leftTurnSpeed = 0.16
        self.backwardSpeed = -0.18
        self.safeSpeed = 0.17

        sleep(0.5)
        self.outP.send({'action': 'MCTL', 'speed': self.forwardSpeed, 'steerAngle': 0.0})

    def make_command(self, steer_angle=0.0, speed=0.17, stop=False, debugInfo = 'Forward: '):
        if stop:
            data = {'action': 'BRAK', 'steerAngle': float(0)}
        else:
            data = {'action': 'MCTL', 'speed': float(speed), 'steerAngle': float(steer_angle)}
        self.logger.debug(debugInfo + str(data))
        return data

    # from here are basic moving commands
    def forward(self, steer, speed=0.18):
        max_steer = 0.5
        if steer > max_steer:
            steer = max_steer
        elif steer < -max_steer:
            steer = -max_steer
        self.outP.send(self.make_command(steer, speed, debugInfo='Forward: '))

    def backward(self, speed=-0.18, steer=0.0, time=0.5):
        self.outP.send(self.make_command(stop=True, debugInfo='Backward: '))        
        self.outP.send(self.make_command(steer_angle=steer, speed=speed, debugInfo='Bakcward: '))
        sleep(time)
        self.outP.send(self.make_command(stop=True, debugInfo='Backward: '))

    def stop(self, time=2.0):
        self.outP.send(self.make_command(stop=True, debugInfo='Stop: '))
        sleep(time)

    def left_turn(self, steer_angle=0.0, speed=0.18,
                  start_point=(0,0), end_point=(0,0), radius=1.035, arc=False):
        """ If arc is true the car will take the angles based on the end points of the curve and the radius """

        if arc:     # hard code something
            pass  # cannot be implemented without the imu sensor
        else:
            self.outP.send(self.make_command(steer_angle, speed, debugInfo='TurnLeft: '))

    def right_turn(self, steer_angle=0.0, speed=0.17,
                   start_point=(0,0), end_point=(0,0), radius=0.665, arc=False):
        """ If arc is true the car will take the angles based on the end points of the curve and the radius """

        if arc:     # hard code something
            pass # cannot be implemented without the imu sensor
        else:
            self.outP.send(self.make_command(steer_angle, speed, debugInfo='TurnRight: '))

    # from here are maneuvers
    def stop_maneuver(self, waiting_time):
        self.stop(waiting_time)
        self.outP.send(self.forward(speed=self.startSpeed, steer=0))

    def pedestrian_crossing_maneuver(self, ang):
        self.outP.send(self.forward(steer=ang, speed=self.safeSpeed))

    def parking_maneuver(self):
        self.outP.send(self.forward(0.0, self.safeSpeed))
        sleep(1)
        self.outP.send(self.stop(0.1))
        self.outP.send(self.backward(speed=self.backwardSpeed, steer=19.5, time=0.5))
        self.outP.send(self.stop(0.1))
        self.outP.send(self.backward(speed=self.backwardSpeed, steer=-19.5, time=0.5))
        self.outP.send(self.stop(1))
        # TODO: implement the maneuver to get out of the parking spot

    def normal_driving(self, lines, dist_from_right, dist_from_left, steer_ang):
        if lines == 2 and dist_from_right > self.allowedDistanceFromLine \
                and dist_from_left > self.allowedDistanceFromLine:  # moving forward case (with confidence :D )
            offset = abs(dist_from_left - dist_from_right)
            if offset > self.allowedOffset:
                self.forward(steer_ang, speed=self.forwardSpeed)
            self.misreadings = 0

        elif lines == 2:  # moving forward case (without confidence :D )
            if steer_ang != 0:
                angle = steer_ang / abs(steer_ang) * 5
            else:
                angle = 0
            self.outP.send(self.make_command(steer_angle=angle, speed=self.safeSpeed))
            self.misreadings = 0

        elif lines == 10:  # turn left case
            if dist_from_right < self.allowedDistanceFromLine:  # this means that its going outside the lines
                self.left_turn(steer_ang, speed=self.leftTurnSpeed)
                pass  # needs an avoidance strategy
            else:
                self.left_turn(steer_ang, speed=self.leftTurnSpeed)
            self.misreadings = 0

        elif lines == 11:  # turn right case
            if dist_from_left < self.allowedDistanceFromLine:  # this means that its going outside the lines
                self.right_turn(steer_ang, speed=self.rightTurnSpeed)
                pass  # needs an avoidance strategy
            else:
                self.right_turn(steer_ang, speed=self.rightTurnSpeed)
                self.misreadings = 0

        elif lines == 0:  # no lines detected
            """ 
            -count how many times this happens and if it happens more than a threshold
             value move backwards in order to go back between the lines
            -count in order to avoid some misreadings
            -in the future -> implement intersection crossing 
             """
            self.misreadings += 1
            if self.misreadings == self.allowedMisreadings:
                self.backward(speed=self.backwardSpeed, time=1)
                self.misreadings = 0

    def intersection_crossing(self, direction):
        self.stop(1)
        if direction == 'left':
            self.left_turn(steer_angle=15.0, speed=self.leftTurnSpeed)
            sleep(1)
        elif direction == 'right':
            self.right_turn(steer_angle=20.0, speed=self.rightTurnSpeed)
            sleep(1)
        elif direction == 'straight':
            self.forward(0, self.safeSpeed)
            sleep(1)

    def run(self):
        while self._running:

            steer_ang, lines, dist_from_right, dist_from_left, horizontal_line = self.inQs[0].get()
            self.logger.debug('Control: steering angle: ' + str(steer_ang))
            self.logger.debug('Control: lines: ' + str(lines) + ', dist right: ' + str(dist_from_right) +
                              ', dist left: ' + str(dist_from_left))
            sign = 0  # = self.inPs[0].recv()
            # stop = 1; prioritate = 2; parcare = 3; trecere = 4; nimic = 0

            if not horizontal_line:
                if sign == 0:    # it goes normal
                    self.normal_driving(lines, dist_from_right, dist_from_left, steer_ang)

                elif sign == 1:     # stops at the sign
                    self.stop_maneuver(2)

                elif sign == 2:     # parking maneuver
                    self.parking_maneuver()

                elif sign == 3:     # slow down and search for pedestrian -- latter not implemented yet
                    self.pedestrian_crossing_maneuver(steer_ang)
            else:  # detected the horizontal line before an intersection => intersection crossing maneuver
                # TODO: add path planning to know where to go in intersection
                # TODO: add check mechanism to be sure that the line detected is indeed the one from the intersection
                self.intersection_crossing("straight")


