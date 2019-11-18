#!/usr/bin/python
#
# Copyright 2018, 2019 Graham Jones
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import serial
import sys
import time


class LakeshoreTempLog():
    ''' Simple interface to a Lakeshore 218 Temperature Logger
    '''

    ERRVAL = -999  # Value to be returned on error.
    NSAMP = 20
    commentStr = ""
    ser2 = None
    isConnected = False

    def __init__(self,
                 port='COM10',
                 timeoutVal=0.5,
                 outf=None,
                 debug = False):
        """ Connect to the temperature logger
        """
        self.debug = debug
        ## Open port to the logger
        try:
            self.ser2 = serial.Serial(port,
                                      9600,
                                      bytesize=serial.SEVENBITS,
                                      parity=serial.PARITY_EVEN,
                                      stopbits=serial.STOPBITS_ONE,
                                      dsrdtr=False,
                                      timeout=timeoutVal)
            self.isConnected = True
        except serial.SerialException:
            print("ERROR - LakeshoreTempLog - Could Not Open Serial Port %s" % port)
            self.ser2 = None
            self.isConnected = False
            # raise NameError('COULD NOT OPEN SERIAL PORT!')

        if (self.isConnected):
            print('No initialisation required...')

        else:
            print("ERROR: ser2==None: Not initialising meter")

    def readTempCh(self,chNo):
        """ Read the current temperature of channel number chNo """
        if (self.isConnected):
            temp_str_3 = self.sendCmd("CRDG? %d\r\n" % chNo)
            print(temp_str_3)
            result = float(temp_str_3)
        else:
            print("ERROR - no connection to DVM")
            result = self.ERRVAL
        return(result)

    def readTempAll(self):
        """ Returns an array of all of the current temperature values. """
        results = []
        temp_str_3 = self.sendCmd("CRDG? 0\r\n")[:-3]
        readings = temp_str_3.split(',')
        temps = ''
        print(temp_str_3)
        for temp in readings:
            results.append(float(temp))

        return(results)

    def close(self):
        """ read any remaining data from the serial port and close it.
        """
        print("LakeShoreTempLog.close()")
        if (self.isConnected):
            retVal = self.toStr(self.ser2.read(1))
            while(retVal != ''):
                print(retVal)
                retVal = self.toStr(self.ser2.read(1))
            self.ser2.close()
            self.ser2 = None
            self.isConnected = False
        else:
            print("already disconnected - doing nothing")
        print("LakeShoreTempLog Connection Closed")
    
    def toStr(self, inStr):
        """ convert a string-like variable inStr into a simple
        ascii encoded string.
        It is complicated by the difference between Python2 and Python3
        behaviour.....
        """
        # if (self.debug): print("toStr - inStr=%s" % inStr)
        if sys.version_info >= (3, 0, 0):
            if isinstance(inStr, bytes):
                outStr = str(inStr, 'ascii')
            else:
                outStr = inStr.encode('ascii')
        else:
            if isinstance(inStr, unicode):
                outStr = str(inStr)
            else:
                outStr = inStr
        return(outStr)

    def sendCmd(self, cmd):
        """ sends a command to the multimeter and returns the result """
        if (self.ser2 is not None):
            self.sendCmdNoWait(cmd)
            retStr = ""
            # chop the CR/LF off the end?
            #retStr = str(self.ser2.read(100))[:-2]
            retStr = self.ser2.read(100).decode('utf-8')[:-2]
            if (self.debug): print("Return value is %s" % retStr)
            return retStr
        else:
            return -1

    def sendCmdNoWait(self, cmd):
        """ sends a command to the multimeter without waiting for a reply """
        if (self.ser2 is not None):
            cmd = self.toStr(cmd)
            if (self.debug): print("Sending %s" % cmd)
            self.ser2.write(cmd)
        else:
            print("ERROR: sendCmdNoWait: self.ser is NONE")


if __name__ == '__main__':
    print("LakeShoreTempLog main()")


    try:
        tLogger = LakeshoreTempLog('/dev/ttyUSB1', debug=True)
        t = tLogger.readTempCh(1)
        print(t)
        t = tLogger.readTempAll()
        print(t)

    finally:
        print("#########################")
        print("finally block")
        sys.stdout.flush()
        tLogger.close()

    print("Done!")
    



