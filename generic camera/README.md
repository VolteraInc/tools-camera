# Python with OpenCV #

You need to install the following...

* Python 2.7.X 
* numpy (it works with 1.10.4)
* PySerial
* OpenCV 3.X (I used 3.1.0)
* A USB camera that works without needing additional drivers

Here is a tutorial on installing OpenCV 3.1.0 for python. http://docs.opencv.org/3.1.0/d5/de5/tutorial_py_setup_in_windows.html#gsc.tab=0

For everything else there's *pip install*.


##Scripts##

There are four scripts that you can directly run with python. There are:


- #testcameracode.py#
    - run this code with the USB camera plugged in to see whether the camera would work with the rest of the code. If it is successful, a window should pop up, and it would show whatever the camera sees (in Canny).
- #autoCalibration.py#
    - run this code with the USB camera plugged in to find the coordinates of the four fiducials on the calibration board.
- #findXYSwitch.py#
    - run this code with the USB camera plugged in to find the coordinates of the XY switch.
- #findZSwitch.py#
    - run this code with the USB camera plugged in to find the coordinates of the Z switch.

Most of the scripts above depend on *com.py* and *openCVCamera.py*. *com.py* contains some functions that communicates with the printer, while *openCVCamera.py* contains image processing algorithms.


###Running the scripts###

To run any of the four scripts mentioned above, just do the following:

```bash
$ python autoCalibration.py
```

Replace *autoCalibration.py* with the name of the script that you want to run.