#used for printer calibration purposes
#this script aligns the camera with the fiducials on the calibration board and prints the coordinates that the fiducials are at

import sys
import com
import openCVCamera as camera
import KxKyTheta
import cv2
import re

 #Initiate our device object - handles serial communication
device = com.Device()
device.connect()

# Extract our initial estimates from a file.
x, y = [], []
x_count = [0,0,0,0]
y_count = [0,0,0,0]
with open('autoCalibrationStartingCoordinates.txt', 'r') as ins:
    x = map(float, ins.readline().split(' '))
    y = map(float, ins.readline().split(' '))

# Confirm the right camera is plugged in. 
capture = cv2.VideoCapture(0) # 1 uses the second camera on the computer (0 is usually a laptop's built-in webcam)
ret, testImage = capture.read()
try:
     cv2.cvtColor(testImage, cv2.COLOR_BGR2GRAY)
except:
    capture = cv2.VideoCapture(1)
    ret, testImage = capture.read()
    try:
        cv2.cvtColor(testImage, cv2.COLOR_BGR2GRAY)
    except:
        print ("ERROR: there are no cameras plugged in")
        sys.exit()


ret, imgOriginal = 0, 0
referenceImg = cv2.imread("images/SingleFiducial.png")

print("Resetting Kx, Ky, Theta...")
device.sendCommandOK("M506 X1 Y1 A0")
device.sendCommandOK("G28") # Home the system.



for i in range(4):
    device.sendCommandOK("G01 X{:f} Y{:f} Z10 F15000".format(x[i], y[i])) # Travel to our estimate but approach from the origin to make up for backlash.
    device.sendCommandOK("M400")
    # device.sendCommandOK("M18")

    print ("Press Esc with the popup window in focus to close the window.")
    ret, imgOriginal = capture.read() # clear the stored image
    while True:
        #for visual display
        ret, imgOriginal = capture.read()
        feedback_x, feedback_y, template = camera.isFiducialAligned(imgOriginal, referenceImg)
        cv2.imshow("camera", template)

        if cv2.waitKey(10) == 27: # this if statement prevents the window from displaying a grey screen
            cv2.destroyAllWindows()
            break

        # If we are lined up - exit.
        if (feedback_x == 0 and feedback_y == 0):
            # Sample Response: X:5.150000 Y:56.649997 Z:0.000000 E:0.000000 Count X: 5.148098 Y:56.647773 Z:0.000000 Absolute X:512 Y:5688 B:0 H:0,0,0
            resp = device.getCmdResponse("M114", "X:") #
            resp = resp[resp.find("Absolute"):] # we get: Absolute X:512 Y:5688 B:0 H:0,0,0
            numbers = re.findall(r'\d+', resp)
            x_count[i] = int(numbers[0])
            y_count[i] = int(numbers[1])
            break

        # Feedback will be an integer value, with a minimum value of 1
        x[i] += 0.01 * feedback_x
        y[i] += 0.01 * feedback_y

        device.sendCommandOK("G01 X{:f} Y{:f} Z10 F100".format(x[i], y[i]))
        device.sendCommandOK("M400")

    # Save our values but add offset so we always apprach from one side.
    with open('autoCalibrationStartingCoordinates.txt', 'w') as ins:
        ins.write("{:f} {:f} {:f} {:f}\n{:f} {:f} {:f} {:f}\n".format(x[0] -1 , x[1] -1 , x[2] -1, x[3] -1, y[0] -1 , y[1] -1, y[2] -1, y[3] -1))

    print ("P%d: X:%f Y:%f" % (i + 1, x[i], y[i]))
    cv2.destroyAllWindows()

# Release the video capture and destroy all windows.
capture.release()
cv2.destroyAllWindows()

for i in range(4):
    print("Values: X{0} Y{1}".format(x_count[i], y_count[i]))

# Compute our calibration values - We use the absolute number of steps because it is more accurate.
Kx, Ky, theta = KxKyTheta.calculateKxKyTheta(x_count[0], y_count[0], x_count[1], y_count[1], x_count[2], y_count[2], x_count[3], y_count[3])
device.sendCommandOK("M506 X{:f} Y{:f} A{:f}".format(Kx, Ky, theta)) # Save our calibration values.
device.sendCommandOK("G01 X1 Y1 F15000") # Return to home fast
device.sendCommandOK("G28") # Home and exit.
