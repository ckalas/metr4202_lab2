#!/usr/bin/env python
import freenect, frame_convert, cv, cv2
import math, time, os, sys, glob, fiducial
import numpy as np
import ctypes

classifier_rect = cv2.CascadeClassifier("classifiers/rectCup.xml")

def main():

    # call some c functions to speed things up
    utils = ctypes.CDLL('utils.dylib')
    arr = lambda x: (ctypes.c_int * len(x))(*x)

    matrix,dist, origin = initialize() # returns params of fiducial as well
    matrixinv = np.linalg.inv(matrix)
    # Take and save initial frame which will show all matches
    img = cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_BGR2RGB)
    cv2.imwrite("temp.png",img)
    frame = cv2.imread("temp.png")
    origins = []
    count = 0
    try:
        # Take and search i frames for cups
        while(1):
            matches = detect()

            img = cv2.cvtColor(matches[1], cv2.COLOR_BGR2RGB)
            for match in matches[0]:
                x,y,w,h = match
                # If the match is new, draw the rectangle   
                if utils.checkNewPoint(arr(match),arr([int(p[0]) for p in origins]),arr([int(p[1]) for p in origins]), len(origins)):
                #if checkNewPoint(match,origins):
                    x_r,y_r,z,color,height = cupDepth(match,matrixinv, origin,cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
                    if x_r == -1:
                        continue
                    origins.append((x,y,w,h))
                    cv2.circle(frame,(x+w/2,y+h/2), 5, color, thickness=2, lineType=8, shift=0)
                    print "cup {0}: xyzh = {1},{2},{3},{4}".format(count, x_r,y_r,z,height)
                    count += 1
                # Draw a rectangle around the cup
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)

            # Display the live stream and cumulative frame with matches
            vis = np.concatenate((frame, img), axis=1)
            cv2.imshow('Combined', vis)

            k = cv2.waitKey(1)
 
            # clear the stored points and refresh image
            if k == ord('c'):
                os.system('clear')
                origins = []
                count = 0
                img = cv2.cvtColor(freenect.sync_get_video()[0], cv2.COLOR_BGR2RGB)
                cv2.imwrite("temp.png",img)
                frame = cv2.imread("temp.png")

            if k == ord('q'):
                cv2.destroyAllWindows()
                break
    except Exception as e:
        pass

    cv2.destroyWindow('Combined')
    cv2.imshow('Matches', frame)
    cv.MoveWindow('Matches', 500, 250)
    while not cv.WaitKey(1) == 27:
       pass
    cv2.destroyAllWindows()
    sys.exit(0)


""" Loads the calibration matrices and finds the fiducial in the frame.
    @params none
    @return a tuple containing the translation and rotation of the origins
"""
def initialize():
    matrix = np.load('matrix.npz')['mtx']
    dist = np.load('dist.npz')['dist'] 
    while(1):
        ret = fiducial.find(freenect.sync_get_video()[0],matrix,dist)
        if ret[0]:
            break
    print ret[1]
    return (matrix, dist, ret[1])

""" Runs a cascade feature matcher on a new video frame.
    @params none
    @return a list of match coords and the image ([(x,y,w,h)], img)
"""
def detect():
    matches = []
    img = freenect.sync_get_video()[0]
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cups = classifier_rect.detectMultiScale(gray, 1.3, 3)
    for (x,y,w,h) in cups:
        matches.append((x,y,w,h))
    return (matches,img)
    
""" Calculates real world coordinates of cup relative to kinect.
    @params the (x,y,w,h) of cup match and camera matrix already inverted
    @return the real world x,y,z and height of cup
"""
def cupDepth(match,matrixinv, origin, gray):
    d2r = lambda x: x*(math.pi/180)

    # Get a depth map with entries in mm and matched to RGB image
    depth = freenect.sync_get_depth(format=freenect.DEPTH_REGISTERED)[0]
    d = 0
    x,y,w,h = match
    # get all the depth in middle of ROI
    z = depth[y+h/2][x+w/2] / 10.0
    # incase the point is bad find next good point
    fix = 5
    while not z:
        z = depth[y+h/2+ fix][x+w/2+fix] / 10.0
        fix -= 1
    # find the lip of the cup and the start of band
    roi = gray[y:y+h, x:x+w]
    # run canny edge detector and then take a column down centre of cup
    canny = cv2.Canny(roi,59,122)
    index = np.where(canny[0:h,w/2] == 255)
    if (depth[y+5][x+w/2]==0 or depth[y+3][x+w/2]==0 or depth[y+6][x+w/2]==0 or depth[y+7][x+w/2]==0):
        print 'Coffee, ',
    else:
        print 'No coffee, ',
    if index[0][0] < 3:
        y_lip = index[0][1]+y
    else:
        y_lip = index[0][0]+y
    if index[0][-2] - index[0][-1] >= 10:
        y_bottom = index[0][-2]+y
    else:
        y_bottom = index[0][-1]+y

    # Get the real world coordinates relative to camera, then perform homogeneous transform
    # to shift points relative to origin.
    # [XYZ]' = [CAMERA]^-1 . [X_P*Z, Y_P*Z, Z]' 

    cameraCoords = matrixinv.dot(np.array([[(x)*z],[(y)*z],[z]]))
    fiducialCoords = origin.dot(np.vstack([cameraCoords, [1]]))
    x_r = fiducialCoords[0][0]
    y_r = -fiducialCoords[1][0]
    z_r = fiducialCoords[2][0]
    y_rl = -matrixinv.dot(np.array([[(x+w/2)*z],[(y_lip)*z],[z]]))[1][0]
    y_rb = -matrixinv.dot(np.array([[(x+w/2)*z],[(y_bottom)*z],[z]]))[1][0]
    
    # calculate size of cup and return appropriate color
    height = abs (y_rl-y_rb)

    # small/medium/large

    if height < 7.5:
        color = (255,0,0)
        print 'Small'
    elif height > 7.5 and height < 9.39:
        color = (0,255,0)
        print 'Medium'
    else:
        color = (0,0,255)
        print 'Large'
    print 'Camera: ', cameraCoords[0][0], cameraCoords[1][0],z
    print 'Transformed: ', x_r,y_r,z_r

    z_mod = -1*y_r
    y_mod = x_r
    x_mod = -1*z_r

    return (x_mod,y_mod,z_mod, color, height)

""" Checks if a point representing cup has already been drawChessboardCorners.
     Use this only if having issues compiling utils.c as a dynamic library in Linux/Windows.
     (slows system down considerably).
    @params the (x,y,w,h) representing a match, the list of current accepted matches
    @return boolean whether or not the point represents the a new cup
"""
def checkNewPoint(match, origins):
    x,y,w,h = match
    for i in range(-30,30):
        for j in range(-30,30):
            if ((x+i) >= 0 and (x+i) < 480 and (y+j) >= 0 and (y+j) < 620 and (x+i in [int(p[0]) for p in origins]) and (y+j in [int(p[1]) for p in origins])):
                return False
    return True

if __name__ == "__main__":
    main()