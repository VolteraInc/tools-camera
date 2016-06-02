#!/usr/bin/python
# -*- coding: UTF-8 -*-
import serial
import sys
from serial.tools import list_ports
import time

def openSerial(ser, port, baudrate):
    ''' Very Simple - Opens the port, empties crud, sends command, validates response '''

    try:
        if not ser.isOpen():
            # Configure the port and then open it.
            ser.port = port
            ser.baudrate = baudrate
            ser.timeout = 0.5
            ser.open()

        #Loop to allow bootloader to run
        while ser.inWaiting() <= 0:
            pass

        while ser.inWaiting() > 0:
            if ser.readline().startswith("start"):
                return True

    except (serial.serialutil.SerialTimeoutException, serial.serialutil.SerialException): #Catch issues with fixture being offline.
        ser.close()
        return False

    ser.close()
    return False

def getCmdResponse(ser, cmd, query):
    ''' Sends a command, returns the response we are looking for '''
    # We are lookign for a particular response, scan each line.

    # Empty out any existing crud.
    while ser.inWaiting() > 0:
        ser.readline()

    ser.write("{0}\r\n".format(cmd))

    lines = ser.readlines() #Readlines has a built in timeout.

    for line in lines:
        if line.startswith(query):
            return line

    return None

def sendCommandOK(ser, cmd):
    ''' Very dumb logic here. We don't attempt to send information twice - Only works for gCode commands.'''

    while ser.inWaiting() > 0: # Empty out crud.
        ser.readline()

    ser.write("{0}\r\n".format(cmd.strip()))  # Strips just in case.

    for i in xrange(10):
        response = ser.readline()
        if response.startswith("ok"):
            return True

    return False

def list_serial_ports():

    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result