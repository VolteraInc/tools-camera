#used for printer calibration purposes
#this script aligns the camera with the fiducials on the calibration board and prints the coordinates that the fiducials are at

import sys
import com
import openCVCamera as camera
import KxKyTheta
import cv2
import re
import os
from threading import Thread
import time
import random
from KxKyTheta import Cx, Cy

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)



class calibration(object):

    def __init__(self):

        # Connect our printer.
        self.device = com.Device()
        self.device.connect()
        self.device.home()

        # Connect the camera.
        self.capture = self.getCamera()
        self.captureFrame = None

        self.x_count = [0,0,0,0]
        self.y_count = [0,0,0,0]

        self.x = [1.680000, 1.540000, 123.850000, 124.010000]
        self.y = [53.050000, 152.930000, 153.130000, 53.260000]

        # Load our template image.
        self.referenceImg = cv2.imread(resource_path('-6Height.png'))

        # Flag used to kill thread.
        self.exit_thread = False

        # Start our worker thread that captures images.
        self.start()

  #Starts updating the images in a thread
    def start(self):
        self.myThread = Thread(target=self.updateFrame, args=())
        self.myThread.daemon = True
        self.myThread.start()

   # Continually updates the frame
    def updateFrame(self):

        while(self.capture.isOpened()):
            ret, frame = self.capture.read()
            if ret == True:
                self.currentFrame = frame
                #print("captured!")

            # Do we have to exit now?
            if self.exit_thread:
                print("Exiting Thread!")
                return

        print("Camera is not opened!")

    def getCamera(self):
        # Confirm the right camera is plugged in.
        capture = cv2.VideoCapture(1) # 1 uses the second camera on the computer (0 is usually a laptop's built-in webcam)
        ret, testImage = capture.read()
        try:
            cv2.cvtColor(testImage, cv2.COLOR_BGR2GRAY)
        except:
            capture = cv2.VideoCapture(0)
            ret, testImage = capture.read()
            try:
                cv2.cvtColor(testImage, cv2.COLOR_BGR2GRAY)
            except:
                print ("ERROR: there are no cameras plugged in")
                sys.exit()

        return capture


    def spread(self):
        ''' This function measures and saves the X axis backlash '''

        with open("spread.txt", 'w') as f:

            free_x, free_y, x_count, y_count = self.homeIn(self.x[0], self.y[0])
            for i in range(1000):

                # Gets 2 randon numbers so we are approaching from different directions
                adj_x = random.uniform(-1,1) * 2
                adj_y = random.uniform(-1,1) * 2

                # Home in and save the center value.
                x, y, x_count, y_count = self.homeIn(free_x + adj_x, free_y + adj_y)
                f.write("{:f}, {:f}, {:f}, {:f}\n".format(x, y, x_count, y_count))

            self.exit(False)

    def x_backlash(self, skip_exit=False):
        ''' This function measures and saves the X axis backlash '''

        left_x = [0,0,0,0,0]
        right_x = [0,0,0,0,0]
        summation = 0

        print("Finding backlash in X Axis... Resetting saved value.")
        self.device.sendCommandOK("M507 X0.0")

        free_x, free_y, x_count, y_count = self.homeIn(self.x[0], self.y[0])
        for i in range(2):
            left_x[i], y, x_count, y_count = self.homeIn(free_x - 0.5, free_y)
            right_x[i], y, x_count, y_count = self.homeIn(free_x + 0.5, free_y)
            summation = summation + (left_x[i] - right_x[i]) # Our backlash is measured by the difference in our measurements
            print("Recorded backlash in X of {0}".format(left_x[i] - right_x[i]))

        backlash = summation/2.0
        if backlash < 0:
            print("Found a negative X backlash of {0}, probably a mistake !!!".format(backlash))
        else:
            print("Saving Overall Backlash X: {0}".format(backlash))
            self.device.sendCommandOK("M507 X{:f}".format(backlash)) # Save our calibration values.
        self.exit(skip_exit)

    def y_backlash(self, skip_exit=False):
        ''' This function measures and saves the X axis backlash '''

        back_y = [0,0,0,0,0]
        forward_y = [0,0,0,0,0]
        summation = 0

        print("Finding backlash in Y Axis... Resetting saved value.")
        self.device.sendCommandOK("M507 Y0.0")

        free_x, free_y, x_count, y_count = self.homeIn(self.x[0], self.y[0])

        for i in range(2):
            x, back_y[i], x_count, y_count = self.homeIn(free_x, free_y - 0.5)
            y, forward_y[i], x_count, y_count = self.homeIn(free_x, free_y + 0.5)
            summation = summation + (back_y[i] - forward_y[i]) # Our backlash is measured by the difference in our measurements
            print("Recorded backlash in Y of {0}".format(back_y[i] - forward_y[i]))

        backlash = summation/2.0
        if backlash < 0:
            print("Found a negative Y backlash of {0}, probably a mistake !!!".format(backlash))
        else:
            print("Saving Overall Backlash Y: {0}".format(backlash))
            self.device.sendCommandOK("M507 Y{:f}".format(backlash)) # Save our calibration values.
        self.exit(skip_exit)

    def axis_skew(self, skip_exit=False):

        passed = False
        while not passed:

            print("Finding Skew parameters. Resetting Kx, Ky, Theta...")
            self.device.sendCommandOK("M506 X1 Y1 A0")

            for i in range(4):
                self.x[i], self.y[i], self.x_count[i], self.y_count[i] = self.homeIn(self.x[i], self.y[i])

            # After values were collected - output them.
            for i in range(4):
                print("Values: X{0} Y{1}".format(self.x[i], self.y[i]))

            # Compute our calibration values - We use the coordinates because step count includes backlash compensation.
            # Kx, Ky, theta, errors = KxKyTheta.calculateKxKyTheta(self.x_co`unt[0], self.y_count[0], self.x_count[1], self.y_count[1], self.x_count[2], self.y_count[2], self.x_count[3], self.y_count[3])
            Kx, Ky, theta, errors = KxKyTheta.calculateKxKyTheta(self.x[0]*Cx, self.y[0]*Cy, self.x[1]*Cx, self.y[1]*Cy, self.x[2]*Cx, self.y[2]*Cy, self.x[3]*Cx, self.y[3]*Cy)

            # Check our errors - and see if they are too large.
            passed = True
            for error in errors:
                if abs(error) > 0.04:
                    print("Failed. Error is too large: ", error)
                    passed = False

            # Adjust values if we failed so we always approach from the right side.
            if not passed:
                for i in range(4):
                    self.x[i] -= 0.5
                    self.y[i] -= 0.5

        # Release the video capture and destroy all windows.
        self.device.sendCommandOK("M506 X{:f} Y{:f} A{:f}".format(Kx, Ky, theta)) # Save our calibration values.
        self.exit(skip_exit)


    def homeIn(self, initial_x, initial_y):
        ''' This function homes in on the reference Image and breaks after center has been idenfitified. '''
        self.device.sendCommandOK("G01 X{:f} Y{:f} Z-6 F6000".format(initial_x, initial_y)) # Travel to our initial estimate.
        self.device.sendCommandOK("M400")
        time.sleep(0.2)

        x_coord = initial_x
        y_coord = initial_y
        while True:

            # Note - Current frame in the workter thread.
            feedback_x, feedback_y, template = camera.isFiducialAligned(self.currentFrame, self.referenceImg)
            cv2.imshow("camera", template)

            if cv2.waitKey(10) == 27: # this if statement prevents the window from displaying a grey screen
                cv2.destroyAllWindows()
                break

            # If we are lined up - exit.
            if (feedback_x == 0 and feedback_y == 0):
                # Sample Response: X:5.150000 Y:56.649997 Z:0.000000 E:0.000000 Count X: 5.148098 Y:56.647773 Z:0.000000 Absolute X:512 Y:5688 B:0 H:0,0,0
                resp = self.device.getCmdResponse("M114", "X:") #
                numbers = re.findall(r'\d+.\d+', resp)
                x_coord = float(numbers[0])
                y_coord = float(numbers[1])

                resp = resp[resp.find("Absolute"):] # we get: Absolute X:512 Y:5688 B:0 H:0,0,0
                numbers = re.findall(r'\d+', resp)
                x_steps = int(numbers[0])
                y_steps = int(numbers[1])
                break

            # Feedback will be an integer value, with a minimum value of 1
            x_coord += 0.01 * feedback_x
            y_coord += 0.01 * feedback_y

            self.device.sendCommandOK("G01 X{:f} Y{:f} F100".format(x_coord, y_coord))
            self.device.sendCommandOK("M400")
            time.sleep(0.2)

        cv2.destroyAllWindows()
        return x_coord, y_coord, x_steps, y_steps



    def exit(self, skip_exit):

        # If we have a full calibration, we want to skip the exit for some tests
        if skip_exit:
            return

        # Kill the thread.
        self.exit_thread = True
        self.myThread.join()

        # Close the camera.
        self.capture.release()
        cv2.destroyAllWindows()

        # Go to home
        self.device.sendCommandOK("G01 X1 Y1 F7000") # Return to home fast
        self.device.home() # Home and exit.
