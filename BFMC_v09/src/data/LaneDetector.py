import numpy as np
import cv2
from threading import Thread


class LaneDetector(Thread):

    def __init__(self, inP, outP):
        """

        """
        super(LaneDetector, self).__init__()
        self.inP = inP
        self.outP = outP

    def region_of_interest(self, local_img):

        """
        Takes an image and returns a mask with the region of interest
        local_img should be gray
        The region of interest is composed by a triangle and a rectangle
        in the bottom half of the image
        Because we don`t want any detections to be made in the middle of the road
        we used a black triangle to cover that part
        """

        # take the dimensions of the image
        height = local_img.shape[0]
        width = local_img.shape[1]

        # create a black mask
        local_mask = np.zeros_like(local_img)

        # the triangle used for the mask
        # triangle1 = np.array([[(0, int(0.7*height)), (width, int(0.7*height)), (int(width/2), int(0.45*height))]])
        # cv2.fillPoly(local_mask, triangle1, 255)

        # the rectangle used for the mask
        # rectangle = np.array([[(0, height), (0, int(0.7*height)), (width, int(0.7*height)), (width, height)]])
        # cv2.fillPoly(local_mask, rectangle, 255)
        
        rectangle = np.array([[(0, height), (0, int(0.4*height)), (width, int(0.4*height)), (width, height)]])
        cv2.fillPoly(local_mask, rectangle, 255)
        
        # the triangle used for blacking out the middle part
       # triangle2 = np.array([[(int(0.2*width), height), (int(0.8*width), height), (int(width/2), int(0.6*height))]])
        #cv2.fillPoly(local_mask, triangle2, 0)

        #cv2.imshow('test01', local_mask)          # TO BE DELETED!!!!!!!!!!
        return local_mask

    def get_canny(self, local_img):

        """
        Takes an image and returns the canny of that image
        First -> change the image to gray
        Second -> apply a Gaussian Blur on the image to decrease the noise
        Then -> apply the canny edge detection function on the image
        Last -> apply the mask to the canny image
        """
        
        local_canny = cv2.Canny(cv2.GaussianBlur(local_img, (5, 5), 0), 100, 200)
        local_mask = self.region_of_interest(local_img)
        #cv2.imshow('test02', local_mask)          # TO BE DELETED!!!!!!!!!!
        #return cv2.bitwise_and(local_canny, local_mask)  # apply the mask to the canny image
        return local_canny   # when the camera is straiight down
    def make_coordinates(self, local_line, im_shape):
        """
        This function calculates the coordinates based on the slope and the y intercept
        """
        slope = local_line[0]
        intercept = local_line[1]
        height, width = im_shape
        y1 = height
        y2 = int(height * (3 / 5))

        # bound the coordinates within the frame
        # x1 = max(-width, min(2 * width, int((y1 - intercept) / slope)))
        # x2 = max(-width, min(2 * width, int((y2 - intercept) / slope)))

        # Maybe will need change !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        x1 = int((y1 - intercept) / slope)
        x2 = int((y2 - intercept) / slope)
        return np.array([x1, y1, x2, y2])

    def get_lines_coordinates(self, local_img):
        """
        Takes an image and returns the coordinates of the left and right lanes
        local_image is a canny image
        First -> detect the lines using the Hough Transformation which gives the end points of each line
        Second -> divide the lines into two categories based on their position and slope
        Last -> find the average slope for each category and compute the end points for the average line
        Return a numpy array which contains the 2 lanes (right and left)
        """
        detected_lines = cv2.HoughLinesP(local_img, 2, np.pi / 180, 100, np.array([]), minLineLength=20, maxLineGap=5)
        #print(detected_lines)           # TO BE DELETED !!!!!!!!!!!!!!
        #print(type(detected_lines))     # TO BE DELETED !!!!!!!!!!!!!!
        right_fit = []
        left_fit = []
        height, width = local_img.shape

        try:
            detected_lines[0]       # check if there are any detected lines
        except TypeError:
            #print('TypeError')          # TO BE DELETED !!!!!!!!!!!!!!
            return np.array([None, None])

        for line in detected_lines:
            x1, y1, x2, y2 = line[0]
            if x1 == x2:
                continue       # ignore vertical lines
            parameters = np.polyfit((x1, x2), (y1, y2), 1)  # finds a poly of degree 1 that passes through the 2 points
            slope = parameters[0]
            intercept = parameters[1]
            if slope > 0 and x1 > width/2 and x2 > width/2:
                right_fit.append((slope, intercept))
            elif slope < 0 and x1 < width/2 and x2 < width/2:
                left_fit.append((slope, intercept))
            else:
                continue  # we don`t care about the lines that don`t fall under those two categories

        if right_fit:
            right_lane = self.make_coordinates(np.average(right_fit, axis=0), local_img.shape)
        else:
            right_lane = None
        if left_fit:
            left_lane = self.make_coordinates(np.average(left_fit, axis=0), local_img.shape)
        else:
            left_lane = None

        return np.array([right_lane, left_lane])

    def display_lines(self, local_img, local_lines):
        """
        This is a test/debug function which adds the lines over the image
        """
        auxiliary_img = np.zeros_like(local_img)
        right_lane = local_lines[0]
        left_lane = local_lines[1]

        if right_lane is not None:
            l = right_lane
            cv2.line(auxiliary_img, (l[0], l[1]), (l[2], l[3]), (255, 255, 255), 20)

        if left_lane is not None:
            l = left_lane
            cv2.line(auxiliary_img, (l[0], l[1]), (l[2], l[3]), (255, 255, 255), 20)

        return cv2.addWeighted(local_img, 0.6, auxiliary_img, 1, 1)

    def run(self):
        """

        """
        # cap = cv2.VideoCapture('D:\\Cristi\\BoschFutureMobility\\Records\\picam19-02-14-07-08.mp4')  #TO BE DELETED!!!

        # frame = cv2.imread('D:\\Cristi\\BoschFutureMobility\\Records\\testCurba4.png')

        while True:
            data = self.inP.recv()
            frame_copy = data[1]
            lane_coordinates = self.get_lines_coordinates(self.get_canny(frame_copy))
            
            #print('LaneDetector, lane_coord: ' + str(lane_coordinates)) #TO BE DELETED
            self.outP.send((lane_coordinates, frame_copy.shape))
            
            cv2.imshow('test1', frame_copy)
            #display_lane = self.display_lines(frame_copy, lane_coordinates)
            #cv2.imshow('test2', display_lane)

            if cv2.waitKey(1) == 27:
                break

        cv2.destroyAllWindows()


