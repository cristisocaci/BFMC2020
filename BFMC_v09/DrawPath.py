from PathFinding import FindPath
import numpy as np
import cv2 as cv

def iLikePP():
    intersectionNodes = [9, 10, 11, 12, 19, 20, 21, 28, 29, 30]
    terminalNodes = []
    mandatoryNodes = []
    x = int(input("Enter starting node: "))
    terminalNodes.append(x)
    x = int(input("Enter the other node: "))
    terminalNodes.append(x)

    print("Number of mandatory nodes: ")
    size = int(input())
    for i in range(0, size):
        x = int(input("Enter node: "))
        mandatoryNodes.append(x)

    pathfinder = FindPath(mandatoryNodes, terminalNodes, intersectionNodes)
    coords = pathfinder.run()  # coordintes! :)
    map_img = cv.imread("boschMap.jpeg")
    for i in range(0, len(coords) - 1):
        pt1 = ((int)(270 * coords[i][1]), (int)(270 * coords[i][2]))
        pt2 = ((int)(270 * coords[i + 1][1]), (int)(270 * coords[i + 1][2]))
        cv.arrowedLine(map_img, pt1, pt2, (0, 255, 0, 0.5), 4)

    print(terminalNodes)
    print(mandatoryNodes)
    cv.imshow("mapPath", map_img)
    cv.imwrite("boschMapPath.jpeg", map_img)

    cv.waitKey(0)
    cv.destroyAllWindows()

# Python doesn't have a fucking switch case.
choice = 3901283;
while choice != 0:
    print("1. Run a test.")
    print("0. Exit")
    choice = int(input())

    if (choice == 1):
        iLikePP()
    elif(choice == 0):
        print("Finished.")
