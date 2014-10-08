import numpy as np
import cv2

MIN_MATCH_COUNT = 10
fid_width = 4.6 # cm

""" Finds the fiducial marker and returns the homogeneous transform of the marker.
    @params img, mtx, dist (BGR frame, camera intrinsics, camera distortion matrix)
    @return a tuple containing the translation and rotation of the origins
"""
def find(img, mtx, dist):

    try:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        id7 = cv2.imread('images/fiducial/id7.png')
        gray7 = cv2.cvtColor(id7, cv2.COLOR_BGR2GRAY)

        # start using SIFT
        sift = cv2.SIFT()

        kp, des = sift.detectAndCompute(gray,None)
        id7_kp, id7_des = sift.detectAndCompute(gray7, None)

        FLANN_INDEX_KDTREE = 0
        index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
        search_params = dict(checks = 50)

        # debug
        if des is None or id7_des is None:
            return (False, None)

        flann = cv2.FlannBasedMatcher(index_params, search_params)
        matches = flann.knnMatch(id7_des, des, k=2)

        # store all the good matches as per Lowe's ratio test
        good = []
        for m,n in matches:
            if m.distance < 0.7*n.distance:
                good.append(m)

        if len(good) > MIN_MATCH_COUNT:
            src_pts = np.float32([ id7_kp[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst_pts = np.float32([ kp[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)

            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            matchesMask = mask.ravel().tolist()

            h, w = gray7.shape
            
            # draw a square box around the detected fiducial
            pts = np.float32([ [0,0], [0,h-1], [w-1,h-1], [w-1,0] ]).reshape(-1, 1, 2)
            dst = cv2.perspectiveTransform(pts, M)
            cv2.polylines( gray, [np.int32(dst)], True, 255, 3, cv2.CV_AA)

            # Required to allow the solvePnP to work
            objp = np.zeros( (2 * 2, 3), np.float32 )
            objp[1,1:2] = 1
            objp[2,0:2] = 1
            objp[3,0:1] = 1

            ret, rvec, tvec = cv2.solvePnP( objp, dst, mtx, dist)
            return get_transform(ret, tvec, rvec)

        else:
            matchesMask = None

            return (False, None)
    except cv2.error as e:
        return (False,None)

""" Applies some scaling to the values and computes the homogeneous transform.
    @params ret, tvec,rvec (boolean indicating the success solve pnp, translation and rotation vector of marker)
    @return a success value and the homogeneous transform
"""
def get_transform(ret, tvec, rvec):

        linearScale = -4.25

        if ret:
                # xyz values are in cm units
                x, y, z = [p[0]*linearScale for p in tvec]
                x = (x-fid_width/2)
                
                # Offset values
                rotx, roty, rotz = [-p[0] for p in rvec]
                rotx = (rotx-0.27)
                # Homogeneous Transformation
                Homogenous_Transformation = np.array([
                    [np.cos(rotz)*np.cos(roty),
                    np.cos(rotz)*np.sin(roty)*np.sin(rotx)-np.sin(rotz)*np.cos(rotx),
                    np.cos(rotz)*np.sin(roty)*np.cos(rotx)+np.sin(rotz)*np.sin(rotx),
                    x],

                    [np.sin(rotz)*np.cos(roty),
                    np.sin(rotz)*np.sin(roty)*np.sin(rotx)+np.cos(rotz)*np.cos(rotx),
                    np.sin(rotz)*np.sin(roty)*np.cos(rotx)-np.cos(rotz)*np.sin(rotx),
                    y],

                    [-np.sin(roty),
                    np.cos(roty)*np.sin(rotx),
                    np.cos(roty)*np.cos(rotx),
                    z],

                    [0, 0, 0, 1] 
                    ])

                return (True, Homogenous_Transformation)
        else:
                return (False, None)     