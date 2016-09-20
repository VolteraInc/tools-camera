import sys
from calibration import calibration

args = sys.argv

cal = calibration()

if args[1] == "axis_skew":
    print("Calibrating for Axis Skew")
    cal.axis_skew()

elif args[1] == "x_backlash":
    print("Calibrating X Axis Backlash")
    cal.x_backlash()

elif args[1] == "y_backlash":
    print("Calibrating Y Axis Backlash")
    cal.y_backlash()

else:
    print("Calibration Axis Skew and Axis Backlash")
    cal.x_backlash(skip_exit=True)
    cal.y_backlash(skip_exit=True)
    cal.axis_skew()

raw_input("Press Enter to Quit")
