#!/usr/bin/python3

import sys
import os
import logging
from pathlib import Path
from optparse import OptionParser
import psutil
import time
import threading

from LongTermTest import LongTermTest

import platform

class LongTermTestControl():

  def __init__(self):
    self.characTime = time.localtime()
    self.LogFileName = "LongTermScan-%s.log" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))


  def init(self, outputdirectory, pathtocfg):
    #initialize everything
    workDIR = os.getcwd()
    try:
      os.chdir(outputdirectory) #change to output directory
    except FileNotFoundError:
      logging.error("Could not open output directory {0}. Please make sure that the directory already exists!".format(outputdirectory))
    self.initLogger(self.LogFileName)
    os.chdir(workDIR)
    self.checkCfgFile(pathtocfg)

    self.l = LongTermTest(pathtocfg, outputdirectory, workDIR)
    #self.l = LongTermTest(pathtocfg, outputdirectory, workDIR)
    #os.chdir(outputdirectory)
    self.l.init()

    #Check if Security Demon is working in the background (works only for LINUX!!)
    if platform.system() == "Windows":
      logging.warning("Security Demon could not be started! The high voltage could not be ramped down in case of a unforseen crash of the program!")
    else:
      started = False
      securitydemoncommand = "python3 src/SecurityDemon.py -k {0} -i {1} -c {2} &".format(self.l.SerialPortKeithley, self.l.SerialPortIseg, self.l.VoltChannel)
      #print(securitydemoncommand)
      os.system(securitydemoncommand)
      for pid in psutil.pids():
        p = psutil.Process(pid)
        if "python" in p.name() and len(p.cmdline()) > 1 and "SecurityDemon.py" in p.cmdline()[1]:
          logging.info("Security Demon succesfully started")
          started = True
      if not started:
        logging.error("Couldn't start Security Demon. Please check the command '{0}' to start SecurityDemon.py".format(securitydemoncommand))
        sys.exit()


  def initLogger(self, logfile):
    # set up logging to file
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s] %(levelname)-8s %(message)s',
                        datefmt='%H:%M:%S',
                        filename=logfile,
                        filemode='w')
    # define a Handler which writes messages to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # set a format which is simpler for console use
    formatter = logging.Formatter('[%(asctime)s] %(levelname)-8s %(message)s',
                                  datefmt='%H:%M:%S')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)
    logging.info("Welcome to Long Term Test Control!")
    logging.info("Log information will be saved in {0}/{1}".format(outputdirectory,logfile))


  def checkCfgFile(self, PathToConfigFile):
    #Check if config file exists

    cfgFile = Path(PathToConfigFile)
    try:
      absPath = cfgFile.resolve()
    except FileNotFoundError:
      logging.error("Cfg file couldn't be found! Please check if the path {0} is correct.".format(PathToConfigFile))
      logging.info("You can create a default config file with 'createDefaultConfigFile.py'")
    logging.info("Found config file {0}".format(PathToConfigFile))


  def start(self):

    #t1 = threading.Thread(target=self.l.LongTerm())
    #t2 = threading.Thread(target=self.test())
    #t1.start()
    #t2.start()


    self.l.LongTerm()



# main loop
if __name__=='__main__':

  parser = OptionParser("usage: %prog [options]")
  parser.add_option("-d", "--directory", dest="outputdirectory",
                    help="path to directory where the log files will be saved [output]",
                    default="output", type="string", metavar="ODIR")
  parser.add_option("-f", "--configfile", dest="pathtocfg",
                    help="path to config file for Long-Term scan [config/LongTermTestControl.cfg]",
                    default="config/LongTermTestControl.cfg", type="string", metavar="CDIR")
  (options, args) = parser.parse_args()

  outputdirectory = options.outputdirectory
  pathtocfg = options.pathtocfg

  #DEBUG!!!
  #pathtocfg = "LongTermTestControl.cfg"
  lc = LongTermTestControl()
  lc.init(outputdirectory, pathtocfg)
  lc.start()
