import time
import serial
import sys
import glob
import re

'''
The following class takes care of:
-- finding and opening a port
-- Confirming we are connected to a printer
-- Sending a serial command
-- Querying the response of a command
'''

class MyException(Exception):
    pass

class Device(object):
    def __init__(self):
        self._serial = serial.Serial()

    def connect(self):
        ''' Scans for a serial port and opens it - raise exception if we cannot open it. '''

        # If it is already open, confirm it's still alive and return.
        if self._serial.isOpen():
            try:
                self._serial.inWaiting()
                return
            except:
                self._serial.close()

        # Scan ports and connect to it
        ports = self._get_ports()
        if len(ports) == 0:
            raise MyException("Could not find any serial ports!")

        if not self._open_serial(ports[-1]):
            raise MyException("Could not open port {0}".format(ports[-1]))

    def assertConnection(self):
        ''' Confirms a connection is active - closes otherwise and throws an error'''
        try:
            self._serial.inWaiting()
            return
        except:
            self._serial.close() # Close no matter what.
            raise MyException("Serial Connection Failure! Reconnect!")

    def getSerialNumber(self):
        ''' Requests serial number from a connected unit '''

        response =  self.getCmdResponse("M507", "echo: M504 S:")
        m = re.search(r'V1-\d\d-\d\d\d\d', response)

        if m is None:
            raise MyException("No Valid Serial Number found! Expected format V1-##-####")

        return m.group()

    def getCmdResponse(self, cmd, query, timeout = 1):
        ''' Sends a command, returns the response we are looking for '''
        # We are looking for a particular response, scan each line.

        # Empty out any existing crud.
        while self._serial.inWaiting() > 0:
            self._printCmd(self._serial.readline())  #Log this

        self._serial.write("{0}\r\n".format(cmd))

        snapshot = time.clock()
        while(time.clock() - snapshot < timeout):
            lines = self._serial.readlines() #Readlines has a built in timeout.
            for line in lines:
                self._printCmd(line)  #Log this
                if line.startswith(query):
                    return line #Breaks out of loop

        raise MyException("Sent Command: {0} but did not receive response starting with {1}".format(cmd, query))


    def sendCommandOK(self, cmd):
        ''' Very dumb logic here. We don't attempt to send information twice - Only works for gCode commands.'''

        while self._serial.inWaiting() > 0: # Empty out crud.
           self._printCmd(self._serial.readline())  #Log this
        self._printCmd(cmd)
        self._serial.write("{0}\r\n".format(cmd.strip()))  # Strips just in case.

        for i in xrange(40):
            response = self._serial.readline()
            #self._printCmd(response) #Log this
            if response.startswith("ok"):
                return True # We need to just return here.

        raise MyException("Sent Command: {0} but did not receive OK".format(cmd))

    def _open_serial(self, port):
        ''' Very Simple - Opens the port, empties crud, sends command, validates response '''

        # Quick return if we are already open
        if self._serial.isOpen():
            return True

        try:
            # Configure the port and then open it.
            self._serial.port = port
            self._serial.baudrate = 250000
            self._serial.timeout = 0.5
            self._serial.open()

            #Loop to allow bootloader to run
            snapshot = time.clock()
            while self._serial.inWaiting() <= 0 and time.clock() - snapshot < 1:
                pass

            while self._serial.inWaiting() > 0:
                if self._serial.readline().startswith("start"):
                    return True

        except (serial.serialutil.SerialTimeoutException, serial.serialutil.SerialException): #Catch issues with fixture being offline.
            self._serial.close()
            return False

        # We would make it here if we never received a 'start' command
        self._serial.close()
        return False


    def _get_ports(self):
        ''' Gets a list of the available serial ports, works in windows and linux '''
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
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

    def _printCmd(self, cmd):
        print(cmd.strip())



def readFile(fileName, mode = 'rt'):
    with open(fileName, mode) as fin:
        return fin.read()


def writeFile(fileName, contents, mode = 'wt'):
    with open(fileName, mode) as fout:
        return fout.write(contents)
