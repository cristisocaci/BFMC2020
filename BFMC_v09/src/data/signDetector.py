import numpy as np
import cv2 as cv
import joblib
import sklearn
from joblib import dump, load
from threading import Thread

class StopSignDetector(Thread):

    def __init__(self, inP, outP):
        '''
        :)
        '''
        self.winSize = (40, 40)
        self.blockSize = (10, 10)
        self.blockStride = (5, 5)
        self.cellSize = (5, 5)
        self.nbins = 9
        self.derivAperture = 1
        self.winSigma = -1.
        self.histogramNormType = 0
        self.L2HysThreshold = 0.2
        self.gammaCorrection = 1
        self.nlevels = 64
        self.signedGradients = True
        # This is used.
        self.hog = cv.HOGDescriptor(self.winSize, self.blockSize, self.blockStride, self.cellSize, self.nbins,
                                    self.derivAperture, self.winSigma, self.histogramNormType,
                                self.L2HysThreshold, self.gammaCorrection, self.nlevels, self.signedGradients)

        self.params = cv.SimpleBlobDetector_Params()

        self.params.minDistBetweenBlobs = 25
        self.params.minThreshold = 0
        self.params.maxThreshold = 256

        self.params.filterByArea = True
        self.params.minArea = 300
        self.params.maxArea = 3500

        self.params.filterByCircularity = False
        self.params.filterByConvexity = False
        self.params.filterByColor = False
        self.params.filterByInertia = False
        # As is this.
        self.detector = cv.SimpleBlobDetector_create(self.params)
        # And these three.
        self.pca = joblib.load("PCA.joblib")
        self.clf = joblib.load("LDA.joblib")
        self.clf02 = joblib.load("classifierSVM.joblib")

    #====================================================================
    def withinBoundsX(self, coord, img):
        '''
        #Checking to see if the X coordinate is not out of image's bounds.
        '''
        if(coord < 0 or coord > img.shape[1]):
            return 0
        return 1

    def withinBoundsY(self, coord, img):
        '''
        #Checking to see if the X coordinate is not out of image's bounds.
        '''
        if(coord < 0 or coord > img.shape[0]):
            return 0
        return 1
    #=====================================================================

    def detectColorAndCenters(self, img):
        '''
        It detects the color, then uses a simple blob goodness (basically countour finding, but somewhat automated)
        to find regions of interest based on color. There are 3 masks, 1 red, 1 yellow and 1 blue.
        On each mask I find blobs of interest then I store the centers of all of those in an array, if you want to know
        specifics, ask me since I can't write that much here. xoxoxo
        :param img: the fucking image
        :return: centers of all blobs of interest
        '''
        imgHSV = cv.cvtColor(img, cv.COLOR_BGR2HSV)
        imgHSV = cv.GaussianBlur(imgHSV, (5, 5), 0)
        # Range for lower RED
        lower_red = np.array([0, 90, 25])
        upper_red = np.array([5, 255, 255])
        mask1 = cv.inRange(imgHSV, lower_red, upper_red)
        # Range for upper range
        lower_red = np.array([155, 90, 25])
        upper_red = np.array([180, 255, 255])
        mask2 = cv.inRange(imgHSV, lower_red, upper_red)
        # Red mask
        red_det = mask1 + mask2
        # Yellow mask
        yellow_det = cv.inRange(imgHSV, (15, 60, 25), (30, 255, 255))
        # Blue mask
        blue_det = cv.inRange(imgHSV, (95, 100, 25), (140, 250, 250))

        finalMask = red_det + yellow_det + blue_det

        #==============================================================================
        #==============================================================================

        keypoints_red = self.detector.detect(red_det)
        keypoints_yellow = self.detector.detect(yellow_det)
        keypoints_blue = self.detector.detect(blue_det)

        '''red_image = cv.drawKeypoints(red_det, keypoints_red, np.array([]), (0, 0, 255),
                                     cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        yellow_image = cv.drawKeypoints(yellow_det, keypoints_yellow, np.array([]), (0, 255, 0),
                                     cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        blue_image = cv.drawKeypoints(blue_det, keypoints_blue, np.array([]), (255, 0, 0),
                                     cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)'''
        #finalImage = red_image + yellow_image + blue_image
        keypoints_all = keypoints_red + keypoints_yellow + keypoints_blue



        #cv.imshow("finalImage", finalImage)

        return (keypoints_all)
    #===================================================================================
    #===================================================================================
    def detectSign(self, img, watch, centers):
        for points in centers:
            x1 = int(points.pt[0]) - 35
            y1 = int(points.pt[1]) - 35
            x2 = int(points.pt[0]) + 35
            y2 = int(points.pt[1]) + 35

            #This is a bit rough. Through trial and error I figured that there's a chance the ROI is just a bit below/above the
            #correct position, so I make 2 other ROI's, once 16 pixels below and one 16 pixels above. So we check 3 times for each
            #detected countour center.
            for disp in (0, 4):
                if (not self.withinBoundsX(x1, img) or  not self.withinBoundsY(y1+disp, img) or not self.withinBoundsX(x2, img) or not self.withinBoundsY(y2+disp, img)):
                    break
                #The window to check using the HOG.
                roi = img[y1+disp:y2+disp, x1:x2]
                roi = cv.resize(roi, (40, 40), interpolation=cv.INTER_AREA)
                #Computing the HOG and making it so we can give it to the SVM, with PCA.
                descriptor = self.hog.compute(roi)
                descriptor = np.array(descriptor)
                descriptor = descriptor.transpose()
                pca_values = self.pca.transform(descriptor)
                #If the SVM gives a positive response (i.e. it is a sign) we show the image and draw a rectangle around the sign
                #we further process it with the classifier.
                if self.clf02.predict(pca_values) ==
                    '''
                    Succesive detections imeplemented on the receiving end, maybe?
                    '''
                    if(self.clf.predict(descriptor) == 1):
                        self.outP.send(1)
                        #cv.rectangle(watch, (x1, y1 + disp), (x2, y2 + disp), (255, 0, 0), 2)

                    elif (self.clf.predict(descriptor) == 2):
                        self.outP.send(2)
                        #cv.rectangle(watch, (x1, y1 + disp), (x2, y2 + disp), (255, 255, 255), 2)

                    elif (self.clf.predict(descriptor) == 3):
                        self.outP.send(3)
                        #cv.rectangle(watch, (x1, y1 + disp), (x2, y2 + disp), (0, 255, 0), 2)

                    elif (self.clf.predict(descriptor) == 4):
                        self.outP.send(4)
                        #cv.rectangle(watch, (x1, y1 + disp), (x2, y2 + disp), (0, 0, 255), 2)


    #====================================================================================

    def run(self):

        while True:
            '''
            victim - the image I actually do the processing on
            watch - this is where I draw the rectangles and whatnot so it can be tested in practice
            centers - the centers of the regions of interest
            '''
            watch = self.inP.recv()
            # A dirty drick, unsure if still necessary, but I will leave it here.
            victim = watch[0:(int)(watch.shape[0]/2), (int)(watch.shape[1]/2):watch.shape[1]]
            victim = cv.copyMakeBorder(victim, 0, 0, 0, 32, cv.BORDER_REPLICATE)
            # Get the centers.
            centers = self.detectColorAndCenters(watch)
            # Detect and classify the signs.
            self.detectSign(victim, watch, centers)

            if cv.waitKey(1) == 27:
                break

        cv.destroyAllWindows()


