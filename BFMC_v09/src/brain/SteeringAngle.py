import numpy as np
import cv2
import math
from src.utils.templates.threadwithstop import ThreadWithStop

""" to be deleted: made changes to the get_steering_angle function: calculated the distance from the lines """


class SteeringAngle(ThreadWithStop):

    def __init__(self, inP, outQs):
        """
        inP - from lane detector
        outQs[0]: to control (sends the angle, nb of lines and distance to lines)

        """
        super(SteeringAngle, self).__init__()
        self.inP = inP
        self.outQs = outQs        
        self.steering_angle = 0
        self.lines = 2
        self.distFromRight = 0
        self.distFromLeft = 0

    def get_steering_angle(self, img_shape, local_lines):
        """
        This function calculates the steering angle based on the coordinates of the detected lines
        """

        height, width = img_shape

        if local_lines[0] is not None and local_lines[1] is not None:
            rx2 = local_lines[0][2]
            lx2 = local_lines[1][2]
            mid = width // 2
            x_offset = (lx2 + rx2) / 2 - mid
            y_offset = height * 3 // 5

            rx1 = local_lines[0][0]
            ry1 = local_lines[0][1]
            ry2 = local_lines[0][3]
            lx1 = local_lines[1][0]
            ly1 = local_lines[1][1]
            ly2 = local_lines[1][3]

            rslope = (ry2 - ry1) / (rx2 - rx1)
            lslope = (ly2 - ly1) / (lx2 - lx1)
            self.distFromRight = abs(rslope * width / 2 - height - rx1 * rslope + ry1) / math.sqrt(rslope * rslope + 1)
            self.distFromLeft = abs(lslope * width / 2 - height - lx1 * lslope + ly1) / math.sqrt(lslope * lslope + 1)
            self.lines = 2

        elif local_lines[0] is None and local_lines[1] is not None:
            # only left detected

            x1 = local_lines[1][0]
            x2 = local_lines[1][2]
            x_offset = x2 - x1
            y_offset = height * 3 // 5

            y1 = local_lines[1][1]
            y2 = local_lines[1][3]
            slope = (y2-y1)/(x2-x1)
            self.distFromRight = None
            self.distFromLeft = abs(slope*width/2 - height - x1*slope + y1) / math.sqrt(slope*slope + 1)
            self.lines = 11

        elif local_lines[0] is not None and local_lines[1] is None:
            # only right detected

            x1 = local_lines[0][0]
            x2 = local_lines[0][2]
            x_offset = x2 - x1
            y_offset = height * 3 // 5

            y1 = local_lines[0][1]
            y2 = local_lines[0][3]
            slope = (y2 - y1) / (x2 - x1)
            self.distFromRight = abs(slope * width / 2 - height - x1 * slope + y1) / math.sqrt(slope * slope + 1)
            self.distFromLeft = None
            self.lines = 10

        elif local_lines[0] is None and local_lines[1] is None:
            self.distFromRight = None
            self.distFromLeft = None
            self.lines = 0

        return int(math.atan(x_offset / y_offset) * 180.0 / math.pi)

    def stabilize_steering_angle(self,
                                 curr_steering_angle,
                                 new_steering_angle,
                                 lane_lines,
                                 max_angle_deviation_2_lines=2,
                                 max_angle_deviation_1_line=3):
        """
        Stabilize the steering
        If the deviation from the current angle is grater than a maximum value, we use that max value for the deviation
        """
        
        if lane_lines[0] is not None and lane_lines[1] is not None:
            max_angle_deviation = max_angle_deviation_2_lines
        else:
            max_angle_deviation = max_angle_deviation_1_line

        angle_deviation = new_steering_angle - curr_steering_angle

        if abs(angle_deviation) > max_angle_deviation:
            stabilized_angle = int(curr_steering_angle + max_angle_deviation * angle_deviation / abs(angle_deviation))
        else:
            stabilized_angle = new_steering_angle
       
        return stabilized_angle

    def run(self):
        """

        """
        while self._running:
            lane_coordinates, frame_shape = self.inP.recv()
            #print('SteeringAngle: ' + str(frame_shape))  #TO BE DELETED
            self.steering_angle = self.stabilize_steering_angle(self.steering_angle,
                                                                self.get_steering_angle(frame_shape, lane_coordinates),
                                                                lane_coordinates)
            # print('Steering angle1: ' + str(self.steering_angle))
            allowed_steer_ang = 19.5
            if self.steering_angle > allowed_steer_ang:
                self.steering_angle = allowed_steer_ang
            elif self.steering_angle < -allowed_steer_ang:
                self.steering_angle = -allowed_steer_ang
            # print('Steering angle2: ' + str(self.steering_angle))
            if lane_coordinates[0] is None and lane_coordinates[1] is not None:
                # only left detected => negative steering angle
                # self.steering_angle =  abs(self.steering_angle)
                pass
            elif lane_coordinates[0] is not None and lane_coordinates[1] is None:
                # only right detected
                # self.steering_angle = - abs(self.steering_angle)
                pass
            self.outQs[0].put((self.steering_angle, self.lines, self.distFromRight, self.distFromLeft))

