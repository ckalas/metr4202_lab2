import numpy as np
import cv2
import os,sys

if len(sys.argv) != 2:
    print 'Usage: python detect.py <cascade.xml>'
    sys.exit(0)

cascade = cv2.CascadeClassifier('classifiers/'+sys.argv[1])

cap = cv2.VideoCapture(0)

while(True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    # Our operations on the frame come here
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    cups = cascade.detectMultiScale(gray, 1.3, 5)
    for (x,y,w,h) in cups:
	    cv2.rectangle(frame,(x,y),(x+w,y+h),(255,0,0),2)
	    roi_color = frame[y:y+h, x:x+w]
    # Display the resulting frame
    cv2.imshow('frame',frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()