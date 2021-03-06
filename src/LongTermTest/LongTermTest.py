#!/usr/bin/env python3

import imp
import configparser
import sys
import time
import os
import logging
from select import select
import threading
from pathlib import Path
from datetime import datetime

from KeithleyControl import keithley2700
from IsegControl import isegT2DP

import platform
if platform.system() == "Windows":
    import msvcrt

class LongTermTest():

  def __init__(self, pathtocfg, outputdirectory, workDIR):

    """Read in parameter from config file and initialize class variables

      Args:
        * str pathtocfg: path to config file
        * str outputdirectory: path to output directory
        * str workDIR: working directory (directory where program was started)
    """

    self._is_running = True
    # Read settings from config file
    self.config = configparser.ConfigParser()
    self.config.read(pathtocfg)

    logging.info("Read in config file parameters")
    logging.info("-------------------------------")
    logging.info("[SerialPorts]")
    self.SerialPortKeithley = self.config['SerialPorts']['keithley2700']
    logging.info("\tkeithley2700 = {0}".format(self.SerialPortKeithley))
    self.SerialPortIseg = self.config['SerialPorts']['isegt2dp']
    logging.info("\tisegt2dp = {0}".format(self.SerialPortIseg))

    logging.info("[Sensors]")
    self.limleakcurr = abs(float(self.config['Sensors']['limleakcurr']))
    logging.info("\tlimleakcurr = {0}".format(self.limleakcurr))
    self.SensorLabel = []
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel1']))
    logging.info("\tsensorlabel1 = {0}".format(self.SensorLabel[0]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel2']))
    logging.info("\tsensorlabel2 = {0}".format(self.SensorLabel[1]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel3']))
    logging.info("\tsensorlabel3 = {0}".format(self.SensorLabel[2]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel4']))
    logging.info("\tsensorlabel4 = {0}".format(self.SensorLabel[3]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel5']))
    logging.info("\tsensorlabel5 = {0}".format(self.SensorLabel[4]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel6']))
    logging.info("\tsensorlabel6 = {0}".format(self.SensorLabel[5]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel7']))
    logging.info("\tsensorlabel7 = {0}".format(self.SensorLabel[6]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel8']))
    logging.info("\tsensorlabel8 = {0}".format(self.SensorLabel[7]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel9']))
    logging.info("\tsensorlabel9 = {0}".format(self.SensorLabel[8]))
    self.SensorLabel.append(str(self.config['Sensors']['sensorlabel10']))
    logging.info("\tsensorlabel10 = {0}".format(self.SensorLabel[9]))

    logging.info("[DCVoltageScan]")
    self.VoltChannel = int(self.config['DCVoltageScan']['voltchannel'])
    logging.info("\tvoltchannel = {0}".format(self.VoltChannel))
    self.DCVoltage = int(self.config['DCVoltageScan']['dcvoltage'])
    logging.info("\tdcvoltage = {0}".format(self.DCVoltage))
    self.polarity = str(self.config['DCVoltageScan']['polarity'])
    logging.info("\tpolarity = {0}".format(self.polarity))
    self.ScanChannels = str(self.config['DCVoltageScan']['scanchannels'])
    logging.info("\tscanchannels = {0}".format(self.ScanChannels))
    self.VoltageRange = str(self.config['DCVoltageScan']['voltagerange'])
    logging.info("\tvoltagerange = {0}".format(self.VoltageRange))
    self.tbm = int(self.config['DCVoltageScan']['tbm'])
    logging.info("\ttbm = {0}".format(self.tbm))
    self.wet = int(self.config['DCVoltageScan']['writeeachtrigger'])
    logging.info("\twriteeachtrigger = {0}".format(self.wet))
    self.maxtime = float(self.config['DCVoltageScan']['maxtime'])
    logging.info("\tmaxtime = {0}".format(self.maxtime))

    #logging.info("[IVCurves]")
    #self.IVEnable = int(self.config['IVCurves']['enable'])
    #logging.info("\tenable = {0}".format(self.IVEnable))
    #self.IVVoltSteps = int(self.config['IVCurves']['voltagesteps'])
    #logging.info("\tvoltagesteps = {0}".format(self.IVVoltSteps))
    #self.IVSET = int(self.config['IVCurves']['scaneachtrigger'])
    #logging.info("\tscaneachtrigger = {0}".format(self.IVSET))

    logging.info("[HumidityReadout]")
    self.humLevel = int(self.config['HumidityReadout']['humlevel'])
    logging.info("\thumlevel = {0}".format(self.humLevel))
    self.humMntPath = str(self.config['HumidityReadout']['mntpath'])
    logging.info("\tmntpath = {0}".format(self.humMntPath))
    logging.info("-------------------------------")

    self.DataFileExist = False
    self.DataFileFormat = "txt"  # available dataformats: 'txt' (separation by tabs) or 'csv' (separation by commas)
    self.characTime = time.localtime()
    self.diffTime = time.time()
    self.DataFileName = "LongTermScan-%s.%s" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime), self.DataFileFormat)
    self.LogFileName = "data/LongTermScan-%s.log" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))

    self.ChannelToOpen = []     # List containing ports to open after each scanning step
    self.OpenChannels = []      # List containing all opened ports
    self.ScanChannelList = []   # List of integer numbers of channels
    self.NrScannedChannels = 0
    self.InitNrScanChan = 0
    self.InitScanChannelList = []
    self.measuredVoltages = []
    self.R = 400                # R in kOhm

    if outputdirectory[-1] == "/":
      self.outputdirectory = outputdirectory[:-1]
    else:
      self.outputdirectory = outputdirectory
    self.workDIR = workDIR
    self.currentValveStatus = False
    self.currentVoltage = 0

    self.DigChannelsWithOutputByte = [[0]*9, [0]*9, [0]*9, [0]*9]
    self.exitPr = False
    self.ValveCurrentlyOpen = False
    self.ValveDesiredOpen = False
    self.KeithleyOccupied = False
    self.DataFileName = "{0}/{1}".format(self.outputdirectory, self.DataFileName)
    self.HumSaveFile = "{0}/LongTermScan-{1}-HumidityLog.txt".format(outputdirectory, time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))
    self.TempSaveFile = "{0}/LongTermScan-{1}-TemperatureLog.txt".format(outputdirectory, time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))

    if self.DCVoltage > 300:
      logging.error("No voltages over 300 V allowed! Please check your settings!")
      logging.info("Program will end!")
      sys.exit()

   # if self.IVEnable == 1 and self.IVVoltSteps > self.DCVoltage:
   #   logging.error("IV curve measurements are enabled, but voltage step read from config file is larger than the DC voltage of voltage scan!")
   #   logging.info("Program will end!")
   #   sys.exit()


  def init(self):

    """initialize connections to Keithley 2700 and Iseg T2DP

      Returns:
        * True if everything worked fine
    """

    # Open instance of Keithley Control
    self.k = keithley2700(self.SerialPortKeithley, True)
    self.k.init()

    self.i = isegT2DP(self.SerialPortIseg, True)
    self.i.init()

    return True


  def keithleyOccupiedTime(self):

    """check if class variable KeithleyOccupied is true (= an instance of the program is currently writing information in the serial port)
       and set the variable to true as soon as it is possible

       Returns:
        * True
    """
    while self.KeithleyOccupied:
      time.sleep(0.5)
    self.KeithleyOccupied = True
    return True


  def initDCVoltScan(self):

    """configure DC voltage scan on Keithley 2700 (with 7707 Multiplexer card!)
       Scan channels read from config file will be analyzed and digital output channels of multiplexer card will be prepared.
       Scan will be initialized with voltage range read from config file (needs only triggering afterwards to start one measurement).
       DC polarity and voltage will be set at Iseg T2DP.

      Returns:
        * True if everything worked fine
    """

    # Configure Keithley 2700
    self.keithleyOccupiedTime()
    logging.info("Configuring Keithley 2700")
    self.analyseCfgScanChannels()
    self.defDigitalOutputChannels()
    self.k.initDCVoltScan(len(self.ScanChannelList), str(self.ScanChannels), self.VoltageRange, self.DigChannelsWithOutputByte)
    self.KeithleyOccupied = False

    logging.info("Configuring iseg T2DP")
    # Configure isegT2DP
    self.i.setPolarity(self.VoltChannel, self.polarity)
    self.i.setVoltage(self.VoltChannel, self.DCVoltage)
    self.currentVoltage = self.DCVoltage

    return True


  def performOneScan(self, write=True, iv=False):
    """trigger one single scan (after initializing the DC voltage scan with initDCVoltScan())
       Measured values will be saved as configured in the config file
       IV scan not yet implemented!
    """

    if iv:
      print("IV test ist not yet implemented.")
    else:
      # Trigger scan
      self.scanTime = time.time()
      self.keithleyOccupiedTime()
      self.measuredVoltages = (self.k.trigDCVoltScan(len(self.ScanChannelList), self.R))[0]
      self.KeithleyOccupied = False
      if write:
        #self.writeVoltagesToFile()
        self.writeCurrentsToFile()
        self.SaveTemperature();
      # Analyze results
      if self.checkLeakageCurrent():
        if not self.removeChannelsFromScan(): #no more open channels left!
          logging.info("Scan list doesn't contain any more channels. Program will end!")
          logging.info("Long-Term Test Control has finished. Good bye!")
          self.keithleyOccupiedTime()
          self.k.close()
          self.KeithleyOccupied = False
          sys.exit()


  def writeVoltagesToFile(self):
    """write voltages measured after one DC voltage trigger event scan into the output file
       File format can be defined in the config file (.txt with tab separation or .csv).

      Returns:
        * True if everything worked fine
    """

    #os.chdir(self.outputdirectory)
    # Create Data File if not existant with header lines
    if (not self.DataFileExist):
      file = open(self.DataFileName, 'w')
      file.write("#Long Term Test - {0}\n".format(time.strftime("%Y_%m_%d %H:%M:%S", self.characTime)))
      file.write("#Scan parameters: DCVoltage={0}V; Polarity={1}; VoltageRange={2}; tbm={3}; writeeachtrigger={4}; maxtime={5}\n".format(self.DCVoltage, self.polarity, self.VoltageRange, self.tbm, self.wet, self.maxtime))
      file.write("#Scan list: {0}\n".format(self.ScanChannelList))
      file.write("#Time after reference(s)\t")
      for ch in self.ScanChannelList:
        file.write("{0} - U(V)\t".format(self.SensorLabel[(int(ch)%100)-1]))
      file.write("\n")
      self.DataFileExist = True
      file.close()

    # Insert for all closed channels the value 0 to measurements
    saveList = [0]*(int(self.InitNrScanChan)+1)
    counter1 = 0  # counter over measuredVoltages[]
    saveList[0] = (float(self.scanTime - self.diffTime))
    saveList[1] = self.currentVoltage
    for ch in self.ScanChannelList:
      index = self.InitScanChannelList.index(ch)
      if counter1 < len(self.measuredVoltages):
        saveList[index+2] = abs(float(self.measuredVoltages[counter1]))
        counter1 += 1

    file = open(self.DataFileName, 'a')
    file.write("{0:7f}".format(saveList[0]))
    if(self.DataFileFormat == "csv"):
      file.write(",")
    else:
        file.write("\t")
    for zaehler in range(1,self.InitNrScanChan+1):
      file.write("{0:9e}".format(saveList[zaehler]))
      if zaehler != self.InitNrScanChan:
        if(self.DataFileFormat == "csv"):
          file.write(",")
        else:
            file.write("\t")
      else:
        file.write("\n")
    file.close()
    #os.chdir(self.workDIR)
    return True


  def writeCurrentsToFile(self):
    """write currents calculated from the measured voltages after one DC voltage scan trigger event into the output file (Resistance value is hardcoded to 400kOhm as a class variable (R)!!!)
       File format can be defined in the config file (.txt with tab separation or .csv).

      Returns:
        * True if everything worked fine
    """

    #os.chdir(self.outputdirectory)

    # Create CSV File if not existant with header lines
    if (not self.DataFileExist):
      file = open(self.DataFileName, 'w')
      file.write("#Long Term Test - {0}\n".format(time.strftime("%Y_%m_%d %H:%M:%S", self.characTime)))
      file.write("#Scan parameters: DCVoltage={0}V; Polarity={1}; VoltageRange={2}; tbm={3}; writeeachtrigger={4}; maxtime={5}\n".format(self.DCVoltage, self.polarity, self.VoltageRange, self.tbm, self.wet, self.maxtime))
      file.write("#Scan list: {0}\n".format(self.ScanChannelList))
      file.write("Reference time: {0} \t {1}\n".format(datetime.fromtimestamp(self.diffTime).strftime("%H:%M:%S"), self.diffTime))
      file.write("#Time after reference(s)\t")
      file.write("Voltage(V)\t")
      for ch in self.ScanChannelList:
        file.write("{0} - I(A)\t".format(self.SensorLabel[(int(ch)%100)-1]))
      file.write("\n")
      #file.write("#Time after start(s)\t{0} - I(A)\t{1} - I(A)\t{2} - I(A)\t{3} - I(A)\t{4} - I(A)\t{5} - I(A)\t{6} - I(A)\t{7} - I(A)\t{8} - I(A)\t{9} - I(A)\n".format(self.SensorLabel1, self.SensorLabel2, self.SensorLabel3, self.SensorLabel4, self.SensorLabel5, self.SensorLabel6, self.SensorLabel7, self.SensorLabel8, self.SensorLabel9, self.SensorLabel10))
      self.DataFileExist = True
      file.close()

    # Insert for all closed channels the value 0 to measurements
    saveList = [0]*(int(self.InitNrScanChan)+2)
    counter1 = 0  # counter over measuredVoltages[]
    saveList[0] = (float(self.scanTime - self.diffTime))
    saveList[1] = self.currentVoltage
    for ch in self.ScanChannelList:
      index = self.InitScanChannelList.index(ch)
      if counter1 < len(self.measuredVoltages):
        saveList[index+2] = (abs(float(self.measuredVoltages[counter1])/(self.R*1000.)))
        counter1 += 1

    file = open(self.DataFileName, 'a')
    file.write("{0:7f}".format(saveList[0]))
    if(self.DataFileFormat == "csv"):
      file.write(",")
    else:
        file.write("\t")
    file.write("{0:3.1f}".format(saveList[1]))
    if(self.DataFileFormat == "csv"):
      file.write(",")
    else:
        file.write("\t")
    for zaehler in range(2,self.InitNrScanChan+2):
      file.write("{0:9e}".format(saveList[zaehler]))
      if zaehler != self.InitNrScanChan+1:
        if(self.DataFileFormat == "csv"):
          file.write(",")
        else:
            file.write("\t")
      else:
        file.write("\n")
    file.close()
    #os.chdir(self.workDIR)
    return True


  def checkLeakageCurrent(self):
    """check the measured voltages after one trigger event and compare them to the defined threshold current

      Returns:
        * True if at least one sensor exceeded the current threshold
        * False if currents in all sensors are below threshold
    """

    somethingToDo = False
    for zaehler in range(0,len(self.measuredVoltages)):
      if self.measuredVoltages[zaehler]/(self.R*0.001) > (self.limleakcurr*0.001):
        self.ChannelToOpen.append(zaehler)
        logging.warning("Channel @{0} exceeded current limit and will be removed from scan list. ".format(self.ScanChannelList[zaehler]))
        somethingToDo = True

    return somethingToDo


  def removeChannelsFromScan(self):
    """shut down the DC voltage to open the switches of each sensor which leakage current exceeded the current threshold
       Channel will be removed from Scan Channel List at Iseg and Iseg will be reinitialized to wait for the next trigger signal

      Returns:
        * True if everything worked fine
    """

    # Voltage shutdown needed!
    self.i.VoltageShutdown(self.VoltChannel)

    # delete channels with to high current from scan channel list
    for ch in self.ChannelToOpen[::-1]:
      self.updateDigOutChan(self.ScanChannelList[int(ch)])
      del self.ScanChannelList[int(ch)]
      self.OpenChannels.append(int(ch))
    self.ChannelToOpen = []

    if (len(self.ScanChannelList) == 0):
      return False

    # create new Keithley readable list of scan channels
    self.ScanChannels = str(self.ScanChannelList)[1:-1].replace(' ', '')  # delete '[' and ']' at beginning and end of list and space characters


    # initialize DC voltage scan with new list of channels
    self.keithleyOccupiedTime()
    self.k.reset()
    self.KeithleyOccupied = False
    #self.k.initDCVoltScan(len(self.ScanChannelList), str(self.ScanChannels), self.VoltageRange)
    self.initDCVoltScan()

    return True


  def PerformVoltageScans(self, startTime, write=True):
    """coordinate DC voltage scans (triggering events) and when to save data output

      Args:
        * startTime: time of initializing the first DC voltage scan (formatted as the output of time.time())
        * write: boolean to set if data output will be written to output file

      Returns:
        * True if everything worked fine
    """

    counter = 1
    counterIV = 1
    if not self.checkExit(20):
      self.performOneScan(write)
      while (self.checkTime(startTime)):
        timetowait = self.calculateTbm()
        if not self.checkExit(timetowait):
          iv = False
          #if(self.IVEnable == 1):
          #  if (int(counterIV) != int(self.IVSET)):
          #    iv = False
          #    counterIV +=1
          #  else:
          #    iv = True
          #    counterIV = 1
          #    counter = 1
          write = False
          if not iv:
            if (int(counter) != int(self.wet)):
              write = False
              counter += 1
            else:
              write = True
              counter = 1
          self.performOneScan(write, iv)
        else:
          self.exitProgram()
          break
      if not self.checkTime(startTime):
        self.exitPr = True
        logging.info("Maximum time of scan reached. ")
        self.exitProgram()
    else:
      self.exitProgram()
    return True


  def LongTerm(self):
    """main function of the class LongTermTest
       Check if voltage is at zero before starting, wait until desired humidity level is reached, initialize first scan and open four threads to control the system.
       thread1: PerformVoltageScans() to coordinate the trigger events during the Long Term Scan.
       thread2: Humiditycontrol() to control the level of humidity inside the test box and change status of the valve
       thread3: waitForInput() to interact with the user
       thread4: monitorThread() to control the correct working of the other 3 threads and end program in safe way if something goes unexpectedly (voltage ramp down!)

      Returns:
        * True if everything worked fine
    """

    self.checkVoltageatStart()

    logging.info("Please check manually if the HV switch of CH%s is turned on at Iseg T2DP" %(self.VoltChannel))
    while True:
      logging.info("Is the HV switch turned on? [Y]: ")
      HVon = input()
      if HVon == "Y" or HVon == "y":
        logging.info("USER INPUT: %s" %(HVon))
        break

    self.firstReachHumLevel()  # wait until humidity level is reached

    startTime = time.time()
    write = True
    self.initDCVoltScan()
    self.InitNrScanChan = self.NrScannedChannels
    self.InitScanChannelList = self.ScanChannelList[:]

    self.thread1 = threading.Thread(target=self.PerformVoltageScans, args=(startTime, write))
    self.thread2 = threading.Thread(target=self.HumidityControl)
    self.thread3 = threading.Thread(target=self.waitForInput)
    self.thread4 = threading.Thread(target=self.monitorThread)
    self.thread1.start()
    self.thread2.start()
    self.thread3.daemon = True  # program will exit if Thread3 is the last remaining thread
    self.thread3.start()
    self.thread4.start()

    return True


  def monitorThread(self):
    """monitor the 3 other threads defined in LongTerm() to ensure that in case of an unexpected failure of one of the threads, the experiment will be safely shut down!
    """

    while not self.exitPr:
      if (not self.thread1.isAlive() and self.exitPr == False):
        logging.error("Long Term Scan Thread seems to have ended unexpectedly!")
        break
      if (not self.thread2.isAlive() and self.exitPr == False):
        logging.error("Humidity Control seems to have ended unexpectedly!")
        break
      if (not self.thread3.isAlive() and self.exitPr == False):
        logging.error("Input thread seems to have ended unexpectedly!")
        break
    if not self.exitPr:
      logging.warning("One of the features of the program doesn't work properly!")
      if self.thread1.isAlive():
        self.exitPr = True
        sys.exit()
      else:
        self.exitPr = True
        self.i.VoltageShutdown(self.VoltChannel)
        self.k.close()
        logging.info("Voltage is shut down and Keithley is reset. However there occured an unexpected end of the program!")
        logging.warning("Please check the error messages above before starting another scan!")


  def analyseCfgScanChannels(self):
    """Analyse scan channels given in config file and copy them into two correctly formated lists to continue in the program

      Returns:
        * True if everything worked fine
    """

    self.ScanChannelList = []
    if ":" in self.ScanChannels:
      # Find start and end channel
      splitted = self.ScanChannels.split(':')
      try:
        int(splitted[0])
        int(splitted[1])
      except:
        logging.error("Scan channels read from config file are not integer. Please check your settings")
        raise ValueError("Scan channels read from config file are not integer. Please check your settings")
      startChannel = int(splitted[0])
      endChannel = int(splitted[1])
      # Calculate number of scan channels
      self.NrScannedChannels = endChannel-startChannel+1
      # Create list with all scan channels named separately
      self.ScanChannelList = list(range(startChannel, endChannel+1))
      self.ScanChannels = str(self.ScanChannelList)[1:-1].replace(' ', '')  #delete '[' and ']' at beginning and end of list and space characters

    elif "," in self.ScanChannels:
      # Calculate number of scan channels
      splitted = self.ScanChannels.split(',')
      self.NrScannedChannels = len(splitted)
      # Find highest and lowest channel number
      startChannel = 0
      endChannel = 0
      for nr in splitted:
        try:
          int(nr)
        except:
          logging.error("Scan channels read from config file is not an integer. Please check your settings")
          raise ValueError("Scan channels read from config file is not an integer. Please check your settings")
        nr = int(nr)
        if (int(nr/100) == 1):
          startChannel = 110
          endChannel = 101
        elif (int(nr/100) == 2):
          startChannel = 210
          endChannel = 201
        else:
          logging.error("Invalid scan channel read from config file!")
          sys.exit()
        self.ScanChannelList.append(int(nr))
        if nr < startChannel:
          startChannel = nr
        if nr > endChannel:
          endChannel = nr

    else:
      try:
        int(self.ScanChannels)
      except:
        logging.error("Scan channel read from config file is not a integer. Please check your settings")
        raise ValueError("Scan channel read from config file is not a integer. Please check your settings")
      startChannel = int(self.ScanChannels)
      endChannel = int(self.ScanChannels)
      self.ScanChannelList.append(int(self.ScanChannels))
      self.NrScannedChannels = 1
    if self.NrScannedChannels > 10:
      logging.error("Number of channels calculated from config file input is higher than 10. Please check your settings")
      sys.exit()

    if (startChannel/100 == 1):
      if (startChannel < 101 or endChannel > 110):
        logging.error("Invalid scan channel read from config file. Only channels between 101 and 110 are available")
        sys.exit()
    elif (startChannel/200 == 2):
      if (startChannel < 201 or endChannel > 210):
        logging.error("Invalid scan channel read from config file. Only channels between 201 and 210 are available")
    return True


  def defDigitalOutputChannels(self):
    """define initial state of digital output channels corresponding to the analog channels to be measured in the config file

      Returns:
        * Array with name and byte information of digital output channels
    """

    if (int(self.ScanChannelList[0]/100) == 1):
      self.DigChannelsWithOutputByte[0][0] = 111
      self.DigChannelsWithOutputByte[1][0] = 112
      self.DigChannelsWithOutputByte[2][0] = 113
      self.DigChannelsWithOutputByte[3][0] = 114
    elif (int(self.ScanChannelList[0]/100) == 2):
      self.DigChannelsWithOutputByte[0][0] = 211
      self.DigChannelsWithOutputByte[1][0] = 212
      self.DigChannelsWithOutputByte[2][0] = 213
      self.DigChannelsWithOutputByte[3][0] = 214
    else:
      print("Initialization error. Program will end")
      sys.exit()

    for i in self.ScanChannelList:
      if (i == 101 or i == 201):
        self.DigChannelsWithOutputByte[0][1] = 1
      elif (i == 102 or i == 202):
        self.DigChannelsWithOutputByte[0][2] = 1
      elif (i == 103 or i == 203):
        self.DigChannelsWithOutputByte[0][3] = 1
      elif (i == 104 or i == 204):
        self.DigChannelsWithOutputByte[0][4] = 1
      elif (i == 105 or i == 205):
        self.DigChannelsWithOutputByte[0][5] = 1
      elif (i == 106 or i == 206):
        self.DigChannelsWithOutputByte[0][6] = 1
      elif (i == 107 or i == 207):
        self.DigChannelsWithOutputByte[0][7] = 1
      elif (i == 108 or i == 208):
        self.DigChannelsWithOutputByte[0][8] = 1
      elif (i == 109 or i == 209):
        self.DigChannelsWithOutputByte[1][1] = 1
      elif (i == 110 or i == 210):
        self.DigChannelsWithOutputByte[1][2] = 1

    return(self.DigChannelsWithOutputByte)


  def updateDigOutChan(self, channeltoopen):
    """update digital output channels if leakage current of a sensor is higher than the threshold and its switch has to be closed

      Returns:
        * True if everything worked fine
    """

    if (channeltoopen == 101 or channeltoopen == 201):
      self.DigChannelsWithOutputByte[0][1] = 0
    if (channeltoopen == 102 or channeltoopen == 202):
      self.DigChannelsWithOutputByte[0][2] = 0
    if (channeltoopen == 103 or channeltoopen == 203):
      self.DigChannelsWithOutputByte[0][3] = 0
    if (channeltoopen == 104 or channeltoopen == 204):
      self.DigChannelsWithOutputByte[0][4] = 0
    if (channeltoopen == 105 or channeltoopen == 205):
      self.DigChannelsWithOutputByte[0][5] = 0
    if (channeltoopen == 106 or channeltoopen == 206):
      self.DigChannelsWithOutputByte[0][6] = 0
    if (channeltoopen == 107 or channeltoopen == 207):
      self.DigChannelsWithOutputByte[0][7] = 0
    if (channeltoopen == 108 or channeltoopen == 208):
      self.DigChannelsWithOutputByte[0][8] = 0
    if (channeltoopen == 109 or channeltoopen == 209):
      self.DigChannelsWithOutputByte[1][1] = 0
    if (channeltoopen == 110 or channeltoopen == 210):
      self.DigChannelsWithOutputByte[1][2] = 0

    return True


  def initLogger(self, logfile):
    """init logger for an output into the shell and the .log file
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


  def checkTime(self, TimeStart):
    """check if maximum time of the Long Term scan is already reached

      Args:
        * TimeStart: start time of the Long Term scan

      Returns:
        * True if scan can be continued
        * False if maximum scan time is reached
    """
    if time.time() > TimeStart + self.maxtime*3600:
      return False
    return True


  def calculateTbm(self):
    """calculate time to wait for the next trigger event

      Returns:
        * int tbm: time to wait for the next trigger event in seconds
    """
    if self.tbm > 60:
      if time.time() > self.scanTime + self.tbm:
        return 0
      return self.tbm - (time.time()-self.scanTime)
    return self.tbm


  def exitProgram(self):
    """abort scan, shut down voltage and close serial ports to exit program
    """
    self.exitPr = True
    logging.info("Scan will be aborted! Please wait until voltage is shut down and program has ended!")
    self.i.VoltageShutdown(self.VoltChannel)
    logging.info("Long-Term Test Control has finished. Good bye!")
    self.keithleyOccupiedTime()
    if (int(self.ScanChannelList[0]/100) == 1):
      self.k.setDigitalIOChannel("111:112", True)
      self.k.setDigitalOutputByte(112, "00000000")
    elif (int(self.ScanChannelList[0]/100) == 2):
      self.k.setDigitalIOChannel("211:212", True)
      self.k.setDigitalOutputByte(212, "00000000")
    self.k.close()
    self.KeithleyOccupied = False


  def checkVoltageatStart(self):
    """check DC voltage of Iseg T2DP before starting the scan and set it to zero if non zero
    """
    self.i.communicative = False
    if (self.i.getVoltage(self.VoltChannel) != 0):
      logging.warning("Voltage at Iseg was measured to be non zero before starting any scan! Please wait a moment until voltage will reach 0V and program will continue!")
      self.i.setVoltage(self.VoltChannel, 0, 5)
      self.currentVoltage = 0
      logging.info("Voltage reached 0V, Long Term scan will now be initialized!")
    self.i.communicative = True


  # HUMIDITY CONTROL
  def HumidityControl(self):
    """measure humidity level each 3 seconds and set digital output byte to control valve status
    """

    logging.info("HUMIDITY CONTROL: Starting humidity stabilization program")
    #startTime = time.time()
    #file = open(self.HumSaveFile, 'a')
    file = open(self.HumSaveFile, 'a')
    while not self.exitPr:
      hum = self.readHum()
      file = open(self.HumSaveFile, 'a')
      file.write("%2.1f" %(time.time()-self.diffTime))
      file.write("\t")
      file.write(str(hum))
      file.write("\n")
      file.close()
      if hum > self.humLevel + 0.2:
        self.DigChannelsWithOutputByte[1][3] = 1
        self.ValveDesiredOpen = True
      elif hum < self.humLevel - 0.2:
        self.DigChannelsWithOutputByte[1][3] = 0
        self.ValveDesiredOpen = False
      #print("humidity", hum)
      binPattern = ""
      if self.ValveCurrentlyOpen != self.ValveDesiredOpen:
        for i in (self.DigChannelsWithOutputByte[1][::-1]):
          if (int(i) < 99):
            binPattern += str(i)
        self.keithleyOccupiedTime()
        if self.ValveDesiredOpen:
          logging.info("HUMIDITY CONTROL: Opening valve, humidity level reached {0}%".format(hum))
        else:
          logging.info("HUMIDITY CONTROL: Closing valve, humidity level reached {0}%".format(hum))
        self.k.setDigitalOutputByte(self.DigChannelsWithOutputByte[1][0], binPattern, False)
        self.KeithleyOccupied = False
        if self.ValveDesiredOpen == True:
          self.ValveCurrentlyOpen = True
        else:
          self.ValveCurrentlyOpen = False
      time.sleep(3)
    file.close()
    logging.info("HUMIDITY CONTROL: Ending humidity stabilization program")
    return True


  def readHum(self):
    """read humidity level from file stated in the config file

      Returns:
        * float humidity: humidity level
    """

    #print(("{0}/humidity".format(self.humMntPath)))
    #humidity = float(Path("{0}/humidity".format(self.humMntPath)).read_text())
    humidity = float(open(str("{0}/humidity".format(self.humMntPath)), "r").read())
    return humidity


  def firstReachHumLevel(self):
    """wait for humidity level to reach desired value before starting the first voltage measurement
       Will only wait if humidity level is higher than the desired value. If lower the scan will start immediately, but humidity will be stabilized as soon as the desired level is reached.

      Returns:
        * True if everything worked fine
    """
    self.analyseCfgScanChannels()
    currentLevel = self.readHum()
    if (currentLevel - self.humLevel) < -1:
      logging.warning("HUMIDITY CONTROL: Current humidity level is below desired value. However scan will be started and once the humidity level has reached desired value it will be stabilized.")
    if (currentLevel - self.humLevel) > 0:
      # open Valve until desired humidity level is reached
      logging.warning("HUMIDITY CONTROL: Current humidity level is above desired value. Valve will be opened and the start of the scan will be postponed until desired level is reached.")
      logging.info("HUMIDITY CONTROL: Opening valve: ")
      self.keithleyOccupiedTime()
      self.ValveCurrentlyOpen = True
      if (int(self.ScanChannelList[0]/100) == 1):
        self.k.setDigitalIOChannel("111:112", True)
        self.k.setDigitalOutputByte(112, "00000100")
      elif (int(self.ScanChannelList[0]/100) == 2):
        self.k.setDigitalIOChannel("211:212", True)
        self.k.setDigitalOutputByte(212, "00000100")
      self.KeithleyOccupied = False
      startTime = time.time()
      bool = False
      while (time.time() - startTime < 1800):
        currentLevel = self.readHum()
        logging.info("HUMIDITY CONTROL: Current humidity level: {0}%".format(currentLevel))
        if (currentLevel - self.humLevel) <= 0:
          logging.info("HUMIDITY CONTROL: Humidity level sank to the desired level and will be stabilized.")
          bool = True
          break
        time.sleep(3)
      if not bool:
        logging.warning("HUMIDITY CONTROL: Humidity level could not reach desired value. The measurements will be performed with a new humidity level of {0}%!".format(currentLevel))
        self.humLevel = currentLevel
    self.ValveCurrentlyOpen = False

    return True


  # TEMPERATURE CONTROL
  def SaveTemperature(self):
      """Save current temperature value to separate file
      """

      file = open(self.TempSaveFile, 'a')
      temp = self.readTemp()
      file.write("%2.1f" %(self.scanTime-self.diffTime))
      file.write("\t")
      file.write(str(temp))
      file.write("\n")
      file.close()


  def readTemp(self):
      """read temperature level from file stated in the config file (1 wire sensor mounting path)

        Returns:
          * float temperature: temperature level
      """

      temperature = float(open(str("{0}/temperature".format(self.humMntPath)), "r").read())
      return temperature


  def waitForInput(self):
    """wait for input from the user
       Possible inputs are "exit" to exit the program in a safe way and "plot" to show the measured data of the current scan
    """
    print("To plot the leakage current distribution over time type 'plot'. To quit the scan please type 'exit'.")
    while not self.exitPr:
      inp = input()
      if inp == "exit":
        logging.info("USER INPUT: {0}".format(inp))
        self.exitPr = True
        #time.sleep(1)
        #self.exitProgram()
      elif inp == "plot":
        os.system("python3 src/plotLongTermTest2.py {0} {1} {2} &".format(self.DataFileName, self.InitNrScanChan, 0.001*self.limleakcurr))
      else:
        print("To plot the leakage current distribution over time type 'plot'. To quit the scan please type 'exit'.")


  def checkExit(self, timetowait):
    """check every second if the class variable 'exitPr' is set until a maximum time 'timetowait' is reached

      Args:
        * timetowait: time to wait until method will end

      Returns:
        * True if class variable 'exitPr' was set to True during the methods runtime
        * False if class variable 'exitPr' is False

    """
    t = 0
    while t < timetowait:
      if self.exitPr:
        return True
        #sys.exit()
      t += 1
      time.sleep(1)
    return False

#  def IVScan(self):
#    logging.info("Preparing IV-curve measurement")
#    self.i.setVoltage(self.VoltChannel, 0, 10)
#    self.currentVoltage = 0
#    curVol = 0
#    while(curVol + self.IVVoltSteps < self.DCVoltage):
#      curVol = curVol + self.IVVoltSteps
#      self.i.setVoltage(self.VoltChannel, curVol, 1)
#      self.currentVoltage = curVol
#      self.keithleyOccupiedTime()
#      self.performOneScan(True)
#      self.KeithleyOccupied = False
#    logging.info("IV-curve measurement ended")

# main loop
if __name__=='__main__':

  # Instanciate Keithly
  l = LongTermTest("config/LongTermTestControl.cfg", "output", "../")
  l.init()
  l.k.installPseudoCard()
  l.LongTerm()
