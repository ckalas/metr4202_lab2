This program uses a Microsoft Kinect on a *nix system utilizing several open source libraries in Python 2.7x.
To install and run, clone repository locally and install the following with Python support. 

These packages are best installed with a package manager. On OSX Homebrew is recommended.

1) OpenCV 2.4.9
2) Libfreenect
3) Numpy

The files of importance are:

main.py - the main program.
fiducial.py - contains the code for  the calculation of the homogeneous transform, called in main.py
assorted.py - contains fucntions for camera calibration and other image acquiring functions

The supplied numpy arrays (.npz) containing camera calibration results were calculated for one specific kinect, 
it is recommended to use the provided functions to generate your own.