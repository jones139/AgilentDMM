#!/usr/bin/env python
#
# Copyright 2019 Graham Jones
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

import sys
import numpy as np
import time
import os
import argparse

import AgilentDMM

class Test:
    # Defines the COM ports to which the Agilent 34401 DVMS are connected.
    DVM1_PORT = "/dev/ttyUSB0"

    def __init__(self,
                 fname="test.csv",
                 nRec=3600,
                 nSamp=5,
                 debug = False):
        print("Test.__init__()")
        self.debug = debug
        self.fname = fname
        self.nRec = nRec
        self.nSamp = nSamp


    def writeDataToFile(self, fname, time_now, 
                        v1m, v1s):
        """ Writes a set of readings v to the output file.
        """
        tn = time.localtime(time_now)
        dateStr = str(tn[0]) + str(tn[1]).zfill(2) + str(tn[2]).zfill(2)
        timeStr = str(tn[3]).zfill(2) + str(tn[4]).zfill(2) + str(
            tn[5]).zfill(2)
        fp = open(fname, 'a')
        fp.write(timeStr + ", ")
        fp.write('%.1f, %f, %f ' % (time_now, v1m, v1s))
        fp.write("\n")
        fp.close()

    def runTest(self):
        """
        Log DMM readings, averaging nSamp samples per record, and 
        recording nRec records.
        """

        fp = open(self.fname, 'w')
        s = 'time, timestamp, DVM1 Mean (V), DMM1 STD (V)\n'
        fp.write(s)
        fp.close()

        try:
            print("Initialising DVM1")
            dvm1 = AgilentDMM.AgilentDMM(self.DVM1_PORT,
                                         debug=self.debug)

            # Collect Samples
            print(
                "Collecting %d records of Sample "
                "Data"
                % (self.nRec))
            for nrec in range(0, self.nRec):
                time_now = time.time()
                v1, t = dvm1.readVoltsMultiple(self.nSamp)
                v1 = np.asarray(v1)
                m = v1.mean()
                s = v1.std()
                sys.stdout.write("%f (%f) " % (v1.mean(), t))
                sys.stdout.flush()
                self.writeDataToFile(
                    self.fname, time_now, m, s)
            sys.stdout.write("\n")
        finally:
            print("#################")
            print("# finally block #")
            print("#################")
            sys.stdout.flush()
            dvm1.close()

        print("*****************************")
        print("*     FINISHED!!!!          *")
        print("*****************************")


if __name__ == "__main__":
    print("DVMLogger.__main__()")

    parser = argparse.ArgumentParser(description='Log readings from Agilent DMM')
    parser.add_argument('--nRec', type=int, default=500,
                        help='Number of records to record')
    parser.add_argument('--nSamp', type=int, default=3,
                        help='Number of samples to average for each record')
    parser.add_argument('-f', '--fname',  dest='fname',
                        default='DMMLogger.csv',
                        help='Output Filename')
    parser.add_argument('--debug', '-d', default=False,
                        action='store_true', dest='debug',
                        help='Number of records to record')

    args = parser.parse_args()
    args = vars(args)
    print(args)
    t = Test(args['fname'],
             nRec = args['nRec'],
             nSamp = args['nSamp'],
             debug=args['debug'])
    t.runTest()
