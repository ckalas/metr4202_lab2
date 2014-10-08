#!/usr/bin/env python
import freenect, frame_convert, cv, cv2
import math, time, os, sys, glob, fiducial
import numpy as np
import ctypes

""" Returns the calibration parameteres for the kinect.
	@params new - boolean that determines whether to take new calibration images
			or load ones previously taken
	@return the calibration parameters (ret,mtx,dist,rvecs,tvecs)
"""
def calibrate(new):
    if new:
        for i in range(20):
            name = "images/calibration/calib{0}.png".format(i)
            cv2.imwrite(name, freenect.sync_get_video()[0])
            time.sleep(0.5)
    # params = (ret, mtx, dist, rvecs, tvecs)
    params = calculateCalibration()
    return params

""" Takes a video frame from kinect, saves original and performs undistortion.
	Intended to be called in a loop.
	@params camera calibration results mtx, dist and a count number used for naming
	@return undistorted image
"""
def take_and_undistort(mtx,dist,count):
    cv2.imwrite('images/scene/orignal{0}.png'.format(count), freenect.sync_get_video()[0])
    img = cv2.imread('images/scene/orignal{0}.png'.format(count))
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    h,  w = gray.shape[:2]
    newcameramtx, roi=cv2.getOptimalNewCameraMatrix(mtx,dist,(w,h),1,(w,h))
    dst = cv2.undistort(img, mtx, dist, None, newcameramtx)
    x,y,w,h = roi
    dst = dst[y:y+h, x:x+w]
    return dst

""" Calculates the calibration paremeters of the kinect.
	@params none
	@return calibration params (ret,mtx,dist,rvecs,tvecs)
"""
def calculateCalibration():
    pattern_size = (8,6)
    # termination criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((pattern_size[0]*pattern_size[1],3), np.float32)
    objp[:,:2] = np.mgrid[0:pattern_size[0],0:pattern_size[1]].T.reshape(-1,2)
    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.
    images = glob.glob('images/calibration/*.png')
    for fname in images:
        img = cv2.imread(fname)
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        # Find the chess board corners
        ret, corners = cv2.findChessboardCorners(gray,pattern_size, cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH)
        # If found, add object points, image points (after refining them)
        if ret == True:
            objpoints.append(objp)
            cv2.cornerSubPix(gray,corners,(22,22),(-1,-1), criteria)
            imgpoints.append(corners)
            # Draw and display the corners
            cv2.drawChessboardCorners(img, pattern_size, corners,ret)
            cv2.imshow('img',img)
            cv2.waitKey(50)
    cv2.destroyAllWindows()
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1],None,None)
    return (ret,mtx,dist,rvecs,tvecs)

if __name__ == "__main__":
	main()