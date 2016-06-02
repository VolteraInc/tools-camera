import cv2
import numpy as np

tolerance = 2

count = 0
last_x, last_y = 0, 0

capture = cv2.VideoCapture(1)
ret, imgOriginal = capture.read()

img = cv2.imread("patch2.png")

print "The purpose of this program is to test the capabilities of the camera."
print ""
print "With the camera plugged into the computer and pointing down at the calibration board, it shows you how far off a fiducial is from the center of the camera and instructs you on how to move it so that it goes to the centre of the camera."
print ""
print "Press Esc with the popup window in focus to close the window."
raw_input("Press Enter to continue...")
print ""
while True:
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

    imgBlurred = cv2.GaussianBlur(imgGrayscale, (5, 5), 1.8)
    imgCanny = cv2.Canny(imgBlurred, 90, 150)
    _, contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    size = imgOriginal.shape
    drawing = np.zeros(size, dtype=np.uint8)
    cv2.drawContours(drawing, contours, -1, (0, 255, 0), 3)

    template = drawing.copy()
    h, w, channels = img.shape

    meth = 'cv2.TM_CCOEFF'
    method = eval(meth)
    # Apply template Matching
    res = cv2.matchTemplate(img,template,method)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    
    if (count == 5):
        #if camera stopped moving
        if ((abs(last_x - top_left[0]) <= tolerance) and (abs(last_y - top_left[1]) <= tolerance)):
            print "stabilized!"
            offset_x, offset_y = -((top_left[0] + 3*w/4 + 5) - size[1]/2), ((top_left[1] + h/2) - size[0]/2)
            
            if (offset_x == 0 and offset_y == 0):
                print "Perfection!"
            elif (abs(offset_x) <= tolerance and abs(offset_y) <= tolerance):
                print "That's about right. Although you can still do better."
            else:
                print "Move by (%f, %f) to get to the centre." % (offset_x, offset_y)
            
        else:
            print "X: %f Y: %f h:%f w:%f Image - h:%f w:%f" % (last_x, last_y, h, w, size[0], size[1])
    
        last_x, last_y = top_left[0], top_left[1]
        count = 0
    else:
        count += 1
        
    cv2.line(template, (0, imgOriginal.shape[0] /2), (imgOriginal.shape[1], imgOriginal.shape[0] /2), (255,255,255), 5)
    cv2.line(template, (imgOriginal.shape[1] /2, 0), (imgOriginal.shape[1] /2, imgOriginal.shape[0]), (255,255,255), 5)
    
    cv2.rectangle(template,top_left, bottom_right, 255, 2)
    cv2.circle(template, (top_left[0] + 3*w/4 + 5, top_left[1] + h/2), 5, 255, -1)
    
    cv2.imshow("camera", template)
    if cv2.waitKey(10) == 27:
        cv2.destroyAllWindows()
        break

capture.release()
cv2.destroyAllWindows()
