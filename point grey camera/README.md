# Visual Studio 2012 with OpenCV #

You need to install the following...

* Microsoft Visual Studio 2012 Express or Professional - aka vs11 (must be this version)
* OpenCV 3.0.0 (this is the latest version of OpenCV that supports vs11)
* FlyCapture SDK (I used v2.9.3.11 for CM3-U3-13Y3C-CS Chameleon3)
* A point grey camera (This was tested with CM3-U3-13Y3C-CS Chameleon3)

Do the following steps:
1) Install Microsoft Visual Studio 2012.
2) Follow this guide to install OpenCV (https://www.youtube.com/watch?v=7SM5OD2pZKY). The VS and OpenCV versions are different, but the steps are the same.
3) Install the FlyCaptureSDK (https://www.ptgrey.com/support/downloads).
4) Go to the directory on where the FlyCapture SDK is installed. The folder should be called Point Grey Research.
5) Go from Point Grey Research -> FlyCapture2 -> src -> FlyCapture2Test
6) Open FlyCapture2Test\_2012.sln with vs11.
7) Replace the contents of FlyCapture2Test.cpp with the contents of the .cpp file.
8) Follow the instructions from the video in step 2 on how to set up the project with OpenCV.
9) Build the project on Debug with x64. It should run properly.