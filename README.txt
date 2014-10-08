Written by Chris Kalas and Andy Tran, 2014.

This program uses a Microsoft Kinect utilizing several open source libraries in Python 2.7x.
To install and run, clone repository locally and install the following with Python support. 

INSTALL:

These packages are best installed with a package manager. On OSX Homebrew is recommended.

1) OpenCV 2.4.9
2) Libfreenect
3) Numpy

To verify whether the libraries are correctly installed, run kinect_test.py. This program outputs the BGR and Depth
images simaltaneously using OpenCV.

Issues installing these libraries are well discussed online

FILES:

The files of importance are:

main.py - the main program - runs a main loop that detects coffee cups in a scene and classifies them.
fiducial.py - contains the code for  the calculation of the homogeneous transform, called in main.py
assorted.py - contains fucntions for camera calibration and other image acquiring functions

NOTES:

i) Due to the nature of the cascade classifier used to detect cups, this program might not be perfectly calibrated to any
   arbitrary cup. With limited testing however, it does manage to pick up other coffee cups with reasonable success.

ii) The supplied numpy arrays (.npz) containing camera calibration results were calculated for one specific kinect -
	it is recommended to use the provided functions to generate your own.

iii) Lighting conditions can considerably affect results, especially the depth image due to EM interference. The kinect
	 should be placed approximately 30cm or higher above the cups and tilted at an angle. The ideal scene location is between
	 65-120cms from the camera

iv) Because for loops in Python are slow, one of the larger loops was moved to C and imported as a library. This file, utils.c 
	comes precompiled for OSX, to use it on Linux/Windows the C file must be compiled according to the OS (google)