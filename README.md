AgilentDMM
==========

AgilentDMM is a simple python class that provides an interface to an Agilent
34401A Digital Multimeter via a serial link.

It provides the bare minimum interface to configure the meter and read
data from it.

It works with both Python2 and Python3

Dependencies
============
  * pySerial
  * numpy
  
Usage Example
=============
dvm1 = AgilentDMM('dev/ttyUSB0')

vArr, tsamp = dvm1.readVoltsMultiple(nSamp=10)

The above connects to and configures the meter and reads 10 measurements
from it.
vArr is an array of the data, tsamp is the time taken to collect the 10 samples

See DMMLogger.py for more usage.
