#!/usr/bin/python3

import psutil
import logging
from optparse import OptionParser
from KeithleyControl import keithley2700
from IsegControl import isegT2DP
import os

import time


logging.basicConfig(level=logging.DEBUG,
                    format='[%(asctime)s] %(levelname)-8s %(message)s',
                    datefmt='%H:%M:%S',
                    filemode='w')
# define a Handler which writes messages to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
# set a format which is simpler for console use
formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s', 
                              datefmt='%H:%M:%S')
# tell the handler to use this format
console.setFormatter(formatter)

#time.sleep(30)

parser = OptionParser("usage: %prog [options] arg1 arg2")
parser.add_option("-k", "--serportKeithley", dest="serportkeith",
                  help="Serial port to Keithley 2700 [/dev/ttyUSB0]", 
                  default="/dev/ttyUSB0", type="string", metavar="SPK")
parser.add_option("-i", "--serportIseg", dest="serportiseg",
                  help="Serial port to Iseg T2DP [/dev/ttyUSB1]", 
                  default="/dev/ttyUSB1", type="string", metavar="SPI")  
parser.add_option("-c", "--channeliseg", dest="channeliseg",
                  help="Voltage channel used at Iseg T2DP [2]", 
                  default=2, type="int", metavar="CHI")                    
(options, args) = parser.parse_args()
  
serportKeithley = options.serportkeith
serportIseg = options.serportiseg
channeliseg = options.channeliseg

#Find pid of process
for pid in psutil.pids():
    p = psutil.Process(pid)
    if "python" in p.name() and len(p.cmdline()) > 1 and "LongTermTestControl.py" in p.cmdline()[1]:
        process_pid = pid

LTSrunning = True
while LTSrunning:
  LTSrunning = os.path.exists("/proc/{0}".format(process_pid))
  #print(LTSrunning)

iseg = isegT2DP(serportIseg)
iseg.init()
#iseg.setVoltage(channeliseg, 100, 10)
if(iseg.getVoltage(channeliseg, False) != 0):
  logging.critical("LongTermTestControl.py seems to be crashed and sensors are still powered with high voltage!")
  logging.critical("Security Demon will ramp down the voltage and reset setup!")
  logging.critical("Please do not change the setup until the program has ended!")
  iseg.VoltageShutdown(channeliseg)
  keith = keithley2700(serportKeithley)
  keith.init()
  keith.close()
  logging.info("Voltage is shut down and connections to measuring instruments are closed")
logging.info("Security Demon ended.")

      

#keith = keithley2700()
#keith.init()
