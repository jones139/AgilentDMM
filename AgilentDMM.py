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


class AgilentDMM():
    ''' Simple interface to Agilent DMM.
    Implements the bare minimum of commands to get it reading voltages
    '''

    ERRVAL = -999  # Value to be returned on error.
    NSAMP = 20
    commentStr = ""
    ser2 = None
    isConnected = False

    def __init__(self,
                 port='COM10',
                 timeoutVal=0.5,
                 rangeStr='VOLT:DC 10,DEF',
                 outf=None,
                 debug = False):
        """ Connect to the Agilent DMM and configure it to 
        measure using the specified range string (see Agilent manual
        for valid syntax), 
        """
        self.debug = debug
        self.rangeStr = rangeStr
        ## Open port to the Agilent multimeter
        try:
            self.ser2 = serial.Serial(port,
                                      9600,
                                      bytesize=serial.SEVENBITS,
                                      parity=serial.PARITY_EVEN,
                                      stopbits=serial.STOPBITS_TWO,
                                      dsrdtr=True,
                                      timeout=timeoutVal)
            self.isConnected = True
        except serial.SerialException:
            print("ERROR - PdAgilent - Could Not Open Serial Port %s" % port)
            self.ser2 = None
            self.isConnected = False
            # raise NameError('COULD NOT OPEN SERIAL PORT!')

        if (self.isConnected):
            # print('Resetting the meter')
            # retVal = self.sendCmd("*RST")
            # if len(retVal) > 0: print('Received:', retVal)

            # print('Clearing the meter error queue')
            # retVal = self.sendCmd("*CLS")
            # if len(retVal) > 0: print('Received:', retVal)

            print('Putting meter into Remote mode')
            retVal = self.sendCmd("SYST:REM\n")
            if len(retVal) > 0: print('Received:', retVal)

            print('Setting Trigger Source to Immediate')
            retVal = self.sendCmd("TRIG:SOUR IMM\n")
            if len(retVal) > 0: print('Received:', retVal)

            print('Setting Trigger Delay to Zero')
            retVal = self.sendCmd("TRIG:DEL 0\n")
            if len(retVal) > 0: print('Received:', retVal)

            print('Setting NPL Cycles to 10')
            retVal = self.sendCmd("VOLT:NPLC 10\n")
            if len(retVal) > 0: print('Received:', retVal)

            print('Setting Range to %s' % rangeStr)
            retVal = self.sendCmd("CONF:%s\n" % self.rangeStr)
            print("retVal=%s" % retVal)

        else:
            print("ERROR: ser2==None: Not initialising meter")

    def readVolts(self):
        """ Read a single value from DVM and return it as a floating
        point value"""
        if (self.isConnected):
            self.sendCmdNoWait("MEAS:%s\n" % self.rangeStr)
            retVal = self.ser2.readline()
            temp_str = self.toStr(retVal)

            if temp_str[1:] == "9.90000000E+37":
                print('Overload!')
                # winsound.Beep(1000,100)
                result = self.ERRVAL
            else:
                if (self.debug): print(temp_str)
                try:
                    result = float(temp_str)  # Convert to float
                except:
                    print("ERROR - failed to convert %s to float" % temp_str)
                    result = self.ERRVAL
        else:
            print("ERROR - no connection to DVM")
            result = self.ERRVAL
        return(result)

    def readVoltsMultiple(self,nSamp = 5):
        """ Read the requested number of samples from the meter 
        and return as a floating point array
        """
        results = []
        tStart = time.time()
        if (self.isConnected):
            retVal = self.sendCmdNoWait("CONF:%s\n" % self.rangeStr)
            retVal = self.sendCmdNoWait("SAMPLE:COUNT %s\n" % nSamp)
            retVal = self.sendCmdNoWait("READ?\n")
            retVal = self.ser2.readline()
            tEnd = time.time()
            # if (self.debug): print("retVal=%s" % retVal, type(retVal))
            retValStr = self.toStr(retVal)
            # if (self.debug): print("retValStr=%s" % retValStr, type(retValStr))
            retValStrs = retValStr.split(',')
            if (self.debug): print("Read %d values in %f sec" %
                                   (len(retValStrs), tEnd-tStart),
                                   retValStrs,
                                   type(retValStrs))
            for val in retValStrs:
                # if (self.debug): print("val=%s" % val)
                if (val[1:] == "9.90000000E+37"):
                    result = self.ERRVAL
                else:
                    try:
                        result = float(val)  # Convert to float
                    except:
                        result = self.ERRVAL
                results.append(result)
        else:
            results.append(self.ERRVAL)
        tEnd = time.time()
        if (self.debug): print("Returning: ",results)
        return(results, (tEnd-tStart))

    def close(self):
        """ read any remaining data from the serial port and close it.
        """
        print("AgilentDMM.close()")
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
        print("AgilendDMM Connection Closed")
    
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
            retStr = str(self.ser2.read(100))[:-2]
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
    print("AgilentDMM main()")


    try:
        dvm1 = AgilentDMM('/dev/ttyUSB0', debug=True)

        vArr, tsamp = dvm1.readVoltsMultiple()
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)

        v = dvm1.readVolts()
        print(v)

        n=1
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=2
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=3
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=5
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=10
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=20
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=5
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
        n=2
        vArr, tsamp = dvm1.readVoltsMultiple(nSamp=n)
        print("Read %d samples in %.2f seconds" % (len(vArr), tsamp), vArr)
        if (len(vArr) != n): print("ERROR:  Asked for %d samples, got %d" %
                                   (n, len(vArr)))
    finally:
        print("#########################")
        print("finally block")
        sys.stdout.flush()
        dvm1.close()

    print("Done!")
    



