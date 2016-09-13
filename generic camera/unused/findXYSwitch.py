import sys
import serial
import com
import openCVCamera as camera
import numpy as np
import cv2

ser = serial.Serial()
ports = com.list_serial_ports()
if (len(ports) == 0):
    print "No available serial port devices are detected."
    sys.exit()

com.openSerial(ser, ports[-1], 250000)
x, y = 33, 0
capture = cv2.VideoCapture(1) #1 uses the second camera on the computer (0 is usually a laptop's built-in webcam)
ret, imgOriginal = 0, 0
img = cv2.imread("xySwitch.png")
meth = 'cv2.TM_CCOEFF'
method = eval(meth)
tolerance = 2

com.sendCommandOK(ser, "G28") #need to go back to home each time to reduce the amount of backlash from the printer
com.sendCommandOK(ser, "G01 X{:f} Y{:f} Z3 F3000".format(x, y))
com.sendCommandOK(ser, "M400")

print "Press Esc with the popup window in focus to skip the calibration process."
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
    
    feedback_x, feedback_y, template = camera.isXYSwitchAligned(imgOriginal, img)
    cv2.imshow("camera", template)
    
    if cv2.waitKey(10) == 27: #this if statement prevents the window from displaying a grey screen
        cv2.destroyAllWindows()
        break
    #end of display code
    
    if (feedback_x == 0 and feedback_y == 0):
        break
    
    if (feedback_x > 0):
        x += 0.01
    elif (feedback_x < 0):
        x -= 0.01
    if (feedback_y > 0):
        y += 0.01
    elif (feedback_y < 0 and y > 0):
        y -= 0.01
        
    com.sendCommandOK(ser, "G01 X{:f} Y{:f} F3000".format(x, y))
    com.sendCommandOK(ser, "M400")

capture.release()
cv2.destroyAllWindows()
print "Camera centre - X:%f Y:%f" % (x, y)
print "Probe centre - X:%f Y:%f" % (x + 0.5, y + 5.84)
com.sendCommandOK(ser, "M505 I{:f} J{:f}".format(x + 0.5, y + 5.84))
cv2.destroyAllWindows()
