import numpy as np
import cv2
import time

cap = cv2.VideoCapture(1)
time.sleep(3)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

i = 0
while(True):
    # Capture frame-by-frame
    if not cap.isOpened():
        print("Cap not opened!")
        ret = cap.open(1)
        print("Opened: ", ret)

    ret, frame = cap.read()
    if ret == True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # Our operations on the frame come here
        # Display the resulting frame
        cv2.imshow('frame', frame)
        print("showed frame")
        if cv2.waitKey(30) == ord('q'):
            break;
    else:
        print("ret was false")

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
