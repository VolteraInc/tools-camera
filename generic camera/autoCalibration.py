#used for printer calibration purposes
#this script aligns the camera with the fiducials on the calibration board and prints the coordinates that the fiducials are at

import sys
import serial
import com
import openCVCamera as camera
import KxKyTheta
import numpy as np
import cv2

ser = serial.Serial()
ports = com.list_serial_ports()
if (len(ports) == 0):
    print "No available serial port devices are detected."
    sys.exit()

com.openSerial(ser, ports[-1], 250000)
capture = cv2.VideoCapture(1) #1 uses the second camera on the computer (0 is usually a laptop's built-in webcam)
ret, imgOriginal = 0, 0
img = cv2.imread("patch2.png")
meth = 'cv2.TM_CCOEFF'
method = eval(meth)

x, y = [], []

with open('autoCalibrationStartingCoordinates.txt', 'r') as ins:
    x = map(float, ins.readline().split(' '))
    y = map(float, ins.readline().split(' '))

for a in range(0, 4):
    com.sendCommandOK(ser, "G01 X2 Y2 Z22 F15000")
    com.sendCommandOK(ser, "G28") #need to go back to home each time to reduce the amount of backlash from the printer
    com.sendCommandOK(ser, "G01 X{:f} Y{:f} Z10 F15000".format(x[a], y[a]))
    com.sendCommandOK(ser, "M400")
    
    print "Press Esc with the popup window in focus to close the window."
    ret, imgOriginal = capture.read() #clear the stored image
    while True:
        #for visual display
        ret, imgOriginal = capture.read()
        try:
            imgGrayscale = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
        except: #if the computer does not have a second camera, then it tries to use this computer's built in webcam
            print "Couldn't find a second camera.. Switching to the default camera."
            capture.release()
            capture = cv2.VideoCapture(0)
            ret, imgOriginal = capture.read()
            try:
                imgGrayscale = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
            except:
                print "ERROR: there are no cameras plugged in"
                sys.exit()
        
        feedback_x, feedback_y, template = camera.isFiducialAligned(imgOriginal, img)
        cv2.imshow("camera", template)
        
        if cv2.waitKey(10) == 27: #this if statement prevents the window from displaying a grey screen
            cv2.destroyAllWindows() 
            break
        #end of display code
        
        if (feedback_x == 0 and feedback_y == 0):
            break
        
        if (feedback_x > 0):
            x[a] += 0.01
        elif (feedback_x < 0):
            x[a] -= 0.01
        if (feedback_y > 0):
            y[a] += 0.01
        elif (feedback_y < 0):
            y[a] -= 0.01
            
        com.sendCommandOK(ser, "G01 X{:f} Y{:f} Z10 F15000".format(x[a], y[a]))
        com.sendCommandOK(ser, "M400")
    
    with open('autoCalibrationStartingCoordinates.txt', 'w') as ins:
        ins.write("{:f} {:f} {:f} {:f}\n{:f} {:f} {:f} {:f}\n".format(x[0] - 0.04, x[1] - 0.04, x[2] - 0.04, x[3] - 0.04, y[0] - 0.04, y[1] - 0.04, y[2] - 0.04, y[3] - 0.04))
	
    print "P%d: X:%f Y:%f" % (a + 1, x[a], y[a])
    cv2.destroyAllWindows()

capture.release()
cv2.destroyAllWindows()
Kx, Ky, theta = KxKyTheta.calculateKxKyTheta(x[0] * KxKyTheta.Cx, y[0] * KxKyTheta.Cy, x[1] * KxKyTheta.Cx, y[1] * KxKyTheta.Cy, x[2] * KxKyTheta.Cx, y[2] * KxKyTheta.Cy, x[3] * KxKyTheta.Cx, y[3] * KxKyTheta.Cy)
com.sendCommandOK(ser, "M506 X{:f} Y{:f} A{:f}".format(Kx, Ky, theta))
