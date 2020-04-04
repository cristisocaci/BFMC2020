import numpy as np
import cv2
import time
from threading import Thread


class LaneDetector(Thread):

    def __init__(self, inP, outP):
        """

        """
        super(LaneDetector, self).__init__()
        self.inP = inP
        self.outP = outP


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
        gauss = cv2.GaussianBlur(local_img, (5, 5), 0)
        local_img = cv2.Canny(gauss, 100, 200)
        detected_lines = cv2.HoughLinesP(local_img, 2, np.pi / 180, 100, np.array([]), minLineLength=20, maxLineGap=5)
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
            if slope > 0 and x1 > width/1.75 and x2 > width/1.75:
                right_fit.append((slope, intercept))
            elif slope < 0 and x1 < width/1.75 and x2 < width/1.75:
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
            try:
                cv2.line(auxiliary_img, (l[0], l[1]), (l[2], l[3]), (255, 255, 255), 20)
            except (OverflowError,TypeError):
                pass

        if left_lane is not None:
            l = left_lane
            try:
                cv2.line(auxiliary_img, (l[0], l[1]), (l[2], l[3]), (255, 255, 255), 20)
            except (OverflowError,TypeError):
                pass

        return cv2.addWeighted(local_img, 0.6, auxiliary_img, 1, 1)

    def if_horizontal(self, local_img):
        x,y = local_img.shape
        local_img = local_img[x-700:x-200,y-1200:y-200]
        gray = local_img # cv2.cvtColor(local_img,cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        bw = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C,  cv2.THRESH_BINARY, 15, -2)
        horizontal = np.copy(bw)
        cols = horizontal.shape[1]
        horizontal_size = cols // 7
        horizontalStructure = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_size, 5))
        horizontal = cv2.erode(horizontal, horizontalStructure)
        horizontal = cv2.dilate(horizontal, horizontalStructure)
        _, contours, hier = cv2.findContours(horizontal,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours:
            if 200<cv2.contourArea(cnt)<5000:
                rect = cv2.minAreaRect(cnt)
                box = cv2.boxPoints(rect)
                box = np.int0(box)
                cv2.drawContours(local_img,[cnt],0,(0,255,0),2)
                #cv2.drawContours(horizontal,[cnt],0,255,-1)
                #cv2.putText(local_img, "HORIZONTAL LINE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                return True
        if not contours:
            #cv2.putText(local_img, " NO HORIZONTAL LINE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            return False
            
    # def birdseye(self, local_img):
    #     IMAGE_H = 300
    #     IMAGE_W = 1280
    #     src = np.float32([[0, IMAGE_H], [1207, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    #     dst = np.float32([[569, IMAGE_H], [711, IMAGE_H], [0, 0], [IMAGE_W, 0]])
    #     M = cv2.getPerspectiveTransform(src, dst)
    #     Minv = cv2.getPerspectiveTransform(dst, src)
    #     img = local_img
    #     img = img[550:(550+IMAGE_H), 0:IMAGE_W]
    #     warped_img = cv2.warpPerspective(img, M, (IMAGE_W, IMAGE_H))
    #     return warped_img

    def run(self):
        """

        """
        #cap = cv2.VideoCapture('/home/mgrrr/Documents/dataset/Records/Set1/10.h264')  #TO BE DELETED!!!

        #frame_copy = cv2.imread('D:\\Cristi\\BoschFutureMobility\\Records\\testCurba4.png')
        ts = [0, 0 , False]
        elapsed = 0
        
        while True:
            data = self.inP.recv()
            frame_copy = data[1]
            hor_line = False
            elapsed = 0
            #_, frame_copy = cap.read()
            #frame_copy = imutils.rotate(frame_copy,270)
            x,y = frame_copy.shape
            hline = self.if_horizontal(frame_copy)
            mview = frame_copy[x-700:x-200, y-1200:y-200]
            x = int(x * 50/100) 
            y = int(y * 50/100)
            dim = (x,y)
            frame_copy = cv2.resize(frame_copy, dim, interpolation = cv2.INTER_AREA)
            lane_coordinates = self.get_lines_coordinates(frame_copy)
            self.outP.send((lane_coordinates, frame_copy.shape))
            display_lane = self.display_lines(frame_copy, lane_coordinates)
            #hline = self.if_horizontal(frame)
            if hline == True and ts[2] == False:
                ts[0] = time.time()
                ts[2] = True
            elif hline == True and ts[2] == True:
                ts[1] = time.time()
                elapsed = ts[1] - ts[0]
            if hline == False and ts[2] == True:
                ts[1] = time.time()
                elapsed = ts[1] - ts[0]
                ts = [0,0, False]
            if elapsed > 1.5:
                cv2.putText(display_lane, "HORIZONTAL LINE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                cv2.putText(display_lane, "ELAPSED" + str(elapsed), (40, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                elapsed = 0
                hor_line = True
            #print('LaneDetector, lane_coord: ' + str(lane_coordinates)) #TO BE DELETED
            # x,y,_ = frame_copy.shape
            # mview = frame[x-700:x-200, y-1200:y-200]
            #cv2.imshow('test1', frame_copy)
            #display_lane = self.display_lines(frame_copy, lane_coordinates)
            #cv2.imshow('test2', display_lane)
            #cv2.imshow("testM", mview)

            if cv2.waitKey(1) == 27:
                break

        cv2.destroyAllWindows()

#l1 = LaneDetector(2,3)
#l1.run()