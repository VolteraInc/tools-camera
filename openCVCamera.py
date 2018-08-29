import cv2
import numpy as np

def isFiducialAligned(imgOriginal, pattern):
    x, y = 0, 0


    # Convert to Greyscale, Blur and get Canny
    imgGrayscale = cv2.cvtColor(imgOriginal, cv2.COLOR_BGR2GRAY)
    # cv2.imshow('GrayScale', imgGrayscale)
    imgBlurred = cv2.GaussianBlur(imgGrayscale, (5, 5), 1.8)
    # cv2.imshow('Gaussian Blur', imgBlurred)
    imgCanny = cv2.Canny(imgBlurred, 90, 150)
    # cv2.imshow('Canny', imgCanny)

    # Use Canny to extract contours
    _, contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    size = imgOriginal.shape
    drawing = np.zeros(size, dtype=np.uint8)

    # Draw contours on black image.
    cv2.drawContours(drawing, contours, -1, (0, 255, 0), 3)
    # cv2.imshow('Contours', drawing)

    # Create a copy of our contours drawing, we will add features to the drawing
    template = imgOriginal.copy()
    # template = drawing.copy()
    h, w, channels = pattern.shape

    # Apply template Matching
    res = cv2.matchTemplate(pattern, template, cv2.TM_CCOEFF)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    top_left = max_loc
    bottom_right = (top_left[0] + w, top_left[1] + h)
    centre_of_pattern_x =  top_left[0] + w/2
    centre_of_pattern_y =  top_left[1] + h/2

    # Computer where the center was found.
    offset_x = top_left[0] - (size[1]/2 - w/2)
    offset_y = top_left[1] - (size[0]/2 - h/2)

    # Draw the crosshairs on the screen (centered)
    cv2.line(template, (0, size[0] /2), (size[1], size[0] /2), (255,255,255), 2)
    cv2.line(template, (size[1] /2, 0), (size[1] /2, size[0]), (255,255,255), 2)

    # Draw the template outline on the screen.
    cv2.rectangle(template,top_left, bottom_right, (255, 0, 0), 1)
    cv2.circle(template, (centre_of_pattern_x, centre_of_pattern_y), 3, (255, 0, 0), -1)

    # These are in pixels, so they have to be integers! i.e -1 , 0 , 1
    if offset_x != 0:
        if (offset_x > 0):
            x = -max(1, offset_x/2)
        elif (offset_x < 0):
            x = -min(-1, offset_x/2)

    if offset_y !=0:
        if (offset_y > 0):
            y = max(1, offset_y/2)
        elif (offset_y < 0):
            y = min(-1, offset_y/2)

    return x, y, template
#
# def isZSwitchAligned(imgOriginal, pattern):
#     x, y = 0, 0
#
#     size = imgOriginal.shape
#     drawing = np.zeros(size, dtype=np.uint8)
#
#     template = imgOriginal.copy()
#     h, w, channels = pattern.shape
#
#     meth = 'cv2.TM_CCOEFF'
#     method = eval(meth)
#     # Apply template Matching
#     res = cv2.matchTemplate(pattern,template,method)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#     top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)
#     centre_of_pattern_x, centre_of_pattern_y = top_left[0] + w/2, top_left[1] + h/2
#
#     offset_x, offset_y = (size[1]/2 - centre_of_pattern_x), (centre_of_pattern_y - (size[0]/4 + 30))
#
#     # draw the crosshairs - centered on the screen.
#     cv2.line(template, (0, (size[0] /4) + 30), (size[1], (size[0] /4) + 30), (255,255,255), 3)
#     cv2.line(template, (size[1] /2, 0), (size[1] /2, size[0]), (255,255,255), 3)
#
#     cv2.rectangle(template,top_left, bottom_right, 255, 2)
#     cv2.circle(template, (centre_of_pattern_x, centre_of_pattern_y), 5, 255, -1)
#
#     if (offset_x != 0 or offset_y != 0):
#         #print "Move by (%f, %f) to get to the centre" % (offset_x, offset_y)
#         if (offset_x > 0):
#             x = 1
#         elif (offset_x < 0):
#             x = -1
#
#         if (offset_y > 0):
#             y = 1
#         elif (offset_y < 0):
#             y = -1
#
#     return x, y, template
#
#
# def isXYSwitchAligned(imgOriginal, pattern):
#     x, y = 0, 0
#
#     size = imgOriginal.shape
#     drawing = np.zeros(size, dtype=np.uint8)
#
#     template = imgOriginal.copy()
#     h, w, channels = pattern.shape
#
#     meth = 'cv2.TM_CCOEFF'
#     method = eval(meth)
#     # Apply template Matching
#     res = cv2.matchTemplate(pattern,template,method)
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
#     top_left = max_loc
#     bottom_right = (top_left[0] + w, top_left[1] + h)
#     centre_of_pattern_x, centre_of_pattern_y = top_left[0] + w/2, top_left[1] + h/2
#
#     offset_x, offset_y = (size[1]/2 - centre_of_pattern_x), (centre_of_pattern_y - (size[0]/2))
#     cv2.line(template, (0, (size[0] /2)), (size[1], (size[0] /2)), (255,255,255), 5)
#     cv2.line(template, (size[1] /2, 0), (size[1] /2, size[0]), (255,255,255), 5)
#
#     cv2.rectangle(template,top_left, bottom_right, 255, 2)
#     cv2.circle(template, (centre_of_pattern_x, centre_of_pattern_y), 5, 255, -1)
#
#     if (offset_x != 0 or offset_y != 0):
#         #print "Move by (%f, %f) to get to the centre" % (offset_x, offset_y)
#         if (offset_x > 0):
#             x = 1
#         elif (offset_x < 0):
#             x = -1
#
#         if (offset_y > 0):
#             y = 1
#         elif (offset_y < 0):
#             y = -1
#
#     return x, y, template
