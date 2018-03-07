#!/usr/bin/python3

import sys
import os
from os.path import exists
import logging
from pathlib import Path
from optparse import OptionParser
import time
import threading

from LongTermTest import LongTermTest

import platform

class LongTermTestControl():

  def __init__(self):
    self.characTime = time.localtime()
    self.LogFileName = "LongTermScan-%s.log" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))


  def init(self, outputdirectory, pathtocfg):

    """initialize Long Term control software

      Args:
        * str outputdirectory: path to outputdirectory where *.log and *.txt
          files will be saved
        * str pathtocfg: path to config file
    """

    # Define working directory as main GIT repository path
    workDIR = os.getcwd()
    if workDIR.endswith('\src') or workDIR.endswith('/src'):
      os.chdir("..")
      workDIR = os.getcwd()
    try:
      os.chdir(outputdirectory)  # change to output directory
    except FileNotFoundError:
      logging.error("Could not open output directory {0}. Please make sure that the directory already exists!".format(outputdirectory))

    self.initLogger(self.LogFileName)
    os.chdir(workDIR)
    self.checkCfgFile(pathtocfg)

    # Initialize Long Term Test class
    self.l = LongTermTest(pathtocfg, outputdirectory, workDIR)
    self.l.init()


  def initLogger(self, logfile):

    """initialize logger

      Args:
        * str logfile: name of output log file

      Logger will create a log file and save the output printed in the shell into it.
      It is formatted as "[$(time)] $(levelname) $(message)".
    """

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

    """check if config file exists

      Args:
        * str PathToConfigFile

      Raises:
        * FileNotFoundError if path doesn't exist!
    """

    # check if config file exists
    if not exists(PathToConfigFile):
      logging.error("Cfg file couldn't be found! Please check if the path {0} is correct.".format(PathToConfigFile))
      logging.info("You can create a default config file with 'createDefaultConfigFile.py'")
      raise FileNotFoundError
    logging.info("Found config file {0}".format(PathToConfigFile))


  def start(self):

    """start Long Term Software
    """

    self.l.LongTerm()


if __name__=='__main__':

  # Define command line options to be passed to program
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

  lc = LongTermTestControl()
  lc.init(outputdirectory, pathtocfg)
  lc.start()
