import cv2
import numpy as np
import argparse

# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
#     help="path to the input image")
# ap.add_argument("-o", "--output", required=True,
#     help="path to output trained model")
# args = vars(ap.parse_args())


cap = cv2.VideoCapture(0)

fourcc = cv2.VideoWriter_fourcc(*'DIVX')
out = cv2.VideoWriter('Records/croppedVideo.avi', fourcc, 20.0, (640, 480))

cv2.namedWindow('da', cv2.WINDOW_NORMAL)

i = 0
while cap.isOpened():
    _, frame = cap.read()
    cv2.imshow('da', frame)
    key = cv2.waitKey(0)
    if key == 27:
        break
    elif key == ord('s'):
        i += 1
        cv2.imwrite("output"+str(i)+'.jpg', frame)
    elif key == ord('w'):
        out.write(frame)

cap.release()
out.release()
cv2.destroyAllWindows()
