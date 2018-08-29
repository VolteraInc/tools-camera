import sys
from calibration import calibration

args = sys.argv

cal = calibration()
print("Calibrating Axis Backlash and Axis Skew")
cal.x_backlash(skip_exit=True)
cal.y_backlash(skip_exit=True)
cal.axis_skew()
raw_input("Press Enter to Quit")
