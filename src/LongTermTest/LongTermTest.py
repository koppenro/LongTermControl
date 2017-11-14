#!/usr/bin/python3

import imp
import configparser
import sys
import time
import os
import logging
from select import select
import threading

from KeithleyControl import keithley2700
from IsegControl import isegT2DP

import platform
if platform.system() == "Windows":
    import msvcrt
    
ImportCreateDefaultCfg = imp.load_source('createDefaultCfg', 'createDefaultConfigFile.py')  #Import module to create default config file

class LongTermTest():
  
  def __init__(self, pathtocfg, outputdirectory, workDIR):
    
    #self.initLogger("output/Test.log")
    
    self._is_running = True
    
    #Read settings from config file
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
    
    logging.info("[IVCurves]")
    self.IVEnable = int(self.config['IVCurves']['enable'])
    logging.info("\tenable = {0}".format(self.IVEnable))
    self.IVVoltSteps = int(self.config['IVCurves']['voltagesteps'])
    logging.info("\tvoltagesteps = {0}".format(self.IVVoltSteps))
    self.IVSET = int(self.config['IVCurves']['scaneachtrigger'])
    logging.info("\tscaneachtrigger = {0}".format(self.IVSET))
    
    logging.info("[HumidityReadout]")
    self.humLevel = int(self.config['HumidityReadout']['humlevel'])
    logging.info("\thumlevel = {0}".format(self.humLevel))
    self.humMntPath = str(self.config['HumidityReadout']['mntpath'])
    logging.info("\tmntpath = {0}".format(self.humMntPath))
    logging.info("-------------------------------")
    
    self.DataFileExist = False;
    self.DataFileFormat = "txt" #'txt' (separation by tabs) or 'csv' (separation by commas) available
    self.characTime = time.localtime()
    self.diffTime = time.time()
    self.DataFileName = "LongTermScan-%s.%s" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime), self.DataFileFormat)
    self.LogFileName = "data/LongTermScan-%s.log" %(time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))
    
    self.ChannelToOpen = [] #List containing ports to open after each scanning step
    self.OpenChannels = [] #List containing all opened ports
    self.ScanChannelList = [] #List of integer numbers of channels
    self.NrScannedChannels = 0
    self.InitNrScanChan = 0
    self.InitScanChannelList = []
    self.measuredVoltages = [] 
    self.R = 400  # R in kOhm
    
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
    self.HumSaveFile = "{0}/LongTermScan-{1}-HumidityLog.txt".format(outputdirectory, time.strftime("%Y_%m_%d-%H_%M_%S", self.characTime))
    
    if self.DCVoltage > 300:
      logging.error("No voltages over 300 V allowed! Please check your settings!")
      logging.info("Program will end!")
      sys.exit()
    
    if self.IVEnable == 1 and self.IVVoltSteps > self.DCVoltage:
      logging.error("IV curve measurements are enabled, but voltage step read from config file is larger than the DC voltage of voltage scan!")
      logging.info("Program will end!")
      sys.exit()


  def init(self):
    
    #self.initLogger(self.LogFileName)
    #Open instance of Keithley Control
    self.k = keithley2700(self.SerialPortKeithley, True)
    self.k.init()
    
    self.i = isegT2DP(self.SerialPortIseg, True)
    self.i.init()
  
    return True
    
  
  def keithleyOccupiedTime(self):
    while self.KeithleyOccupied:
      time.sleep(0.5)
    self.KeithleyOccupied = True
    return True
  
  
  def initDCVoltScan(self):
    
    #Configure Keithley 2700
    self.keithleyOccupiedTime()
    logging.info("Configuring Keithley 2700")
    self.analyseCfgScanChannels()
    self.defDigitalOutputChannels()
    self.k.initDCVoltScan(len(self.ScanChannelList), str(self.ScanChannels), self.VoltageRange, self.DigChannelsWithOutputByte)
    self.KeithleyOccupied = False
    
    logging.info("Configuring iseg T2DP")
    #Configure isegT2DP
    self.i.setPolarity(self.VoltChannel, self.polarity)
    self.i.setVoltage(self.VoltChannel, self.DCVoltage)
    self.currentVoltage = self.DCVoltage
    
    return True
  
  
  def performOneScan(self, write=True, iv=False):
    
    if iv:
      print("IV")
    else:
      #Trigger scan
      self.scanTime = time.time()
      self.keithleyOccupiedTime()
      print("VOR TRIGDCVOLTSCAN")
      self.measuredVoltages = (self.k.trigDCVoltScan(len(self.ScanChannelList), self.R))[0]
      print("AFTER TRIGDCVOLTSCAN")
      self.KeithleyOccupied = False
      if write:
        #self.writeVoltagesToFile()
        self.writeCurrentsToFile()
      #Analyse results
      if self.checkLeakageCurrent():
        if not self.removeChannelsFromScan(): #no more open channels left!
          logging.info("Scan list doesn't contain any more channels. Program will end!")
          logging.info("Long-Term Test Control has finished. Good bye!")
          self.keithleyOccupiedTime()
          self.k.close()
          self.KeithleyOccupied = False
          sys.exit()

    
  def writeVoltagesToFile(self):
    
    os.chdir(self.outputdirectory)
    #Create Data File if not existant with header lines
    if (not self.DataFileExist):
      file = open(self.DataFileName, 'w')
      file.write("#Long Term Test - {0}\n".format(time.strftime("%Y_%m_%d %H:%M:%S", self.characTime)))
      file.write("#Scan parameters: DCVoltage={0}V; Polarity={1}; VoltageRange={2}; tbm={3}; writeeachtrigger={4}; maxtime={5}\n".format(self.DCVoltage, self.polarity, self.VoltageRange, self.tbm, self.wet, self.maxtime))
      file.write("#Scan list: {0}\n".format(self.ScanChannelList))
      file.write("#Time after start(s)\t")
      for ch in self.ScanChannelList:
        file.write("{0} - U(V)\t".format(self.SensorLabel[(int(ch)%100)-1]))
      file.write("\n")
      self.DataFileExist = True
      file.close()
    
    #Insert for all closed channels the value 0 to measurements
    saveList = [0]*(int(self.InitNrScanChan)+1)
    counter1 = 0  #counter over measuredVoltages[]
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
    
    os.chdir(self.workDIR)
    
    return True
    
    
  def writeCurrentsToFile(self):
    os.chdir(self.outputdirectory)
    
    #Create CSV File if not existant with header lines
    if (not self.DataFileExist):
      file = open(self.DataFileName, 'w')
      file.write("#Long Term Test - {0}\n".format(time.strftime("%Y_%m_%d %H:%M:%S", self.characTime)))
      file.write("#Scan parameters: DCVoltage={0}V; Polarity={1}; VoltageRange={2}; tbm={3}; writeeachtrigger={4}; maxtime={5}\n".format(self.DCVoltage, self.polarity, self.VoltageRange, self.tbm, self.wet, self.maxtime))
      file.write("#Scan list: {0}\n".format(self.ScanChannelList))
      file.write("#Time after start(s)\t")
      file.write("Voltage(V)\t")
      for ch in self.ScanChannelList:
        file.write("{0} - I(A)\t".format(self.SensorLabel[(int(ch)%100)-1]))
      file.write("\n")
      #file.write("#Time after start(s)\t{0} - I(A)\t{1} - I(A)\t{2} - I(A)\t{3} - I(A)\t{4} - I(A)\t{5} - I(A)\t{6} - I(A)\t{7} - I(A)\t{8} - I(A)\t{9} - I(A)\n".format(self.SensorLabel1, self.SensorLabel2, self.SensorLabel3, self.SensorLabel4, self.SensorLabel5, self.SensorLabel6, self.SensorLabel7, self.SensorLabel8, self.SensorLabel9, self.SensorLabel10))
      self.DataFileExist = True
      file.close()
    
    #Insert for all closed channels the value 0 to measurements
    saveList = [0]*(int(self.InitNrScanChan)+2)
    
    #self.InitScanChannelList
    
    counter1 = 0  #counter over measuredVoltages[]
    
    saveList[0] = (float(self.scanTime - self.diffTime))
    saveList[1] = self.currentVoltage
    for ch in self.ScanChannelList:
      index = self.InitScanChannelList.index(ch)
      if counter1 < len(self.measuredVoltages):
        saveList[index+2] = (abs(float(self.measuredVoltages[counter1])/(400*1000.)))
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
    
    os.chdir(self.workDIR)
    
    return True
    
    
  def checkLeakageCurrent(self):
    
    somethingToDo = False
    for zaehler in range(0,len(self.measuredVoltages)):
      if self.measuredVoltages[zaehler]/(self.R*0.001) > (self.limleakcurr*0.001): 
        self.ChannelToOpen.append(zaehler) 
        logging.warning("Channel @{0} exceeded current limit and will be removed from scan list. ".format(self.ScanChannelList[zaehler]))
        somethingToDo = True
    
    return somethingToDo
    
  
  def removeChannelsFromScan(self):
    
    #Voltage shutdown needed!
    self.i.VoltageShutdown(self.VoltChannel)
    
    #delete channels with to high current from scan channel list
    for ch in self.ChannelToOpen[::-1]:
      #print("Channel: ", ch)
      self.updateDigOutChan(self.ScanChannelList[int(ch)])
      #print(self.ScanChannelList[int(ch)])
      del self.ScanChannelList[int(ch)]
      self.OpenChannels.append(int(ch))
    self.ChannelToOpen = []
    
    if (len(self.ScanChannelList) == 0):
      return False
    
    #create new Keithley readable list of scan channels
    self.ScanChannels = str(self.ScanChannelList)[1:-1].replace(' ', '')  #delete '[' and ']' at beginning and end of list and space characters
    
    
    #initialize DC voltage scan with new list of channels
    self.keithleyOccupiedTime()
    self.k.reset()
    self.KeithleyOccupied = False
    #self.k.initDCVoltScan(len(self.ScanChannelList), str(self.ScanChannels), self.VoltageRange)
    self.initDCVoltScan()
      
    return True  
  
    
  def PerformVoltageScans(self, startTime, write=True):
    testtime = time.time()
    counter = 1
    counterIV = 1
    if not self.checkExit(20):
      self.performOneScan(write)
      while (self.checkTime(startTime)):
        timetowait = self.calculateTbm()
        if not self.checkExit(timetowait):
          iv = False
          if(self.IVEnable == 1):
            if (int(counterIV) != int(self.IVSET)):
              iv = False
              counterIV +=1
            else:
              iv = True
              counterIV = 1
              counter = 1
          write = False
          if not iv:
            if (int(counter) != int(self.wet)):
              write = False
              counter += 1
            else:
              write = True
              counter = 1
          print("VOR PERFORMONESCAN")
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
  
    self.checkVoltageatStart()
      
    logging.info("Please check manually if the HV switch of CH%s is turned on at Iseg T2DP" %(self.VoltChannel))
    while True:
      logging.info("Is the HV switch turned on? [Y]: ")
      HVon = input()
      if HVon == "Y" or HVon == "y":
        logging.info("USER INPUT: %s" %(HVon))
        break
      
    self.firstReachHumLevel() #wait until humidity level is reached
    
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
    self.thread3.daemon = True  #program will exit if Thread3 is the last remaining thread
    self.thread3.start()
    self.thread4.start()
    
    return True
    
   
  def monitorThread(self):
    
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
        self.exitPr = True
      else:
        self.exitPr = True
        #print("SelfExit", self.exitPr)
        self.i.VoltageShutdown(self.VoltChannel)
        self.k.close()
        logging.info("Voltage is shut down and Keithley is reset. However there occured an unexpected end of the program!")
        logging.warning("Please check the error messages above before starting another scan!")
        #sys.exit()
    
  
  def analyseCfgScanChannels(self):
    """Analyse scan channels given in config file and copy them into two correctly formated lists to continue in the program
    """
    
    self.ScanChannelList = []
    if ":" in self.ScanChannels:
      #Find start and end channel
      splitted = self.ScanChannels.split(':')
      try:
        int(splitted[0])
        int(splitted[1])
      except:
        logging.error("Scan channels read from config file are not integer. Please check your settings")
        raise ValueError("Scan channels read from config file are not integer. Please check your settings")
      startChannel = int(splitted[0])
      endChannel = int(splitted[1])
      #Calculate number of scan channels
      self.NrScannedChannels = endChannel-startChannel+1
      #Create list with all scan channels named separately
      self.ScanChannelList = list(range(startChannel, endChannel+1))
      self.ScanChannels = str(self.ScanChannelList)[1:-1].replace(' ', '')  #delete '[' and ']' at beginning and end of list and space characters
      
    elif "," in self.ScanChannels:
      #Calculate number of scan channels
      splitted = self.ScanChannels.split(',')
      self.NrScannedChannels = len(splitted)
      #Find highest and lowest channel number
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


  def input_with_timeout_sane(self, prompt, timeout, default):
      """Read an input from the user or timeout"""
      start_time = time.time()
      print(prompt,)
      sys.stdout.flush()
      rlist, _, _ = select([sys.stdin], [], [], timeout)
      while rlist:
          end_time = time.time()
          time_difference = end_time - start_time
          s = sys.stdin.readline().replace('\n','')
          if(s == "plot"):
            print("KITPlot will be called forked, scan will continue.")
            os.system("python3 src/plot_LongTermTest.py output/{0} {1} {2} &".format(self.DataFileName, self.InitNrScanChan, 0.001*self.limleakcurr))
            rlist, _, _ = select([sys.stdin], [], [], timeout - time_difference)
          elif(s != "exit"):
            print("Please type 'plot' to open KITPlot, 'exit' to quit the program or nothing to continue!")
            rlist, _, _ = select([sys.stdin], [], [], timeout - time_difference)
          else: 
            break
      else:
          s = default
          #print(s)
      return s

  def input_with_timeout_windows(self, prompt, timeout, default): 
      start_time = time.time()
      print(prompt,)
      sys.stdout.flush()
      input = ''
      while True:
          if msvcrt.kbhit():
              chr = msvcrt.getche()
              if ord(chr) == 13: # enter_key
                  print(input)
                  print("Input accepted. Please wait a little moment until it will be progressed. ")
                  time.sleep(timeout - (time.time()-start_time))
                  break
              elif ord(chr) >= 32: #space_char
                  input += chr.decode()
          if len(input) == 0 and (time.time() - start_time) > timeout:
              break
      if len(input) > 0:
          if(input == "plot"):
            print("Plot program will be called forked, scan will continue.")
            os.system("python ../plot_LongTermTest.py data/{0} {1} {2} &".format(self.DataFileName, self.InitNrScanChan, 0.001*self.limleakcurr))  
          print("Input ", input)
          return input
      else:
          return default

  def input_with_timeout(self, prompt, timeout, default=''):
      if platform.system() == "Windows":
          return self.input_with_timeout_windows(prompt, timeout, default)
      else:
          return self.input_with_timeout_sane(prompt, timeout, default)


  def checkTime(self, TimeStart):
    if time.time() > TimeStart + self.maxtime*3600:
      return False
    return True
    
  
  def calculateTbm(self):
    if self.tbm > 60:
      if time.time() > self.scanTime + self.tbm:
        return 0
      return self.tbm - (time.time()-self.scanTime)
    return self.tbm

  
  def exitProgram(self):
    self.exitPr = True
    logging.info("Scan will be aborted! Please wait until voltage is shut down and program has ended!")
    self.i.VoltageShutdown(self.VoltChannel)
    logging.info("Long-Term Test Control has finished. Good bye!")
    self.keithleyOccupiedTime()
    self.k.close()
    self.KeithleyOccupied = False
    #sys.exit()
    
  
  def checkVoltageatStart(self):
    self.i.communicative = False
    if (self.i.getVoltage(self.VoltChannel) != 0):
      logging.warning("Voltage at Iseg was measured to be non zero before starting any scan! Please wait a moment until voltage will reach 0V and program will continue!")
      self.i.setVoltage(self.VoltChannel, 0, 5)
      self.currentVoltage = 0
      logging.info("Voltage reached 0V, Long Term scan will now be initialized!")
    self.i.communicative = True
    
    
  # HUMIDITY CONTROL
  def HumidityControl(self):
    
    logging.info("HUMIDITY CONTROL: Starting humidity stabilization program")
    startTime = time.time()
    file = open(self.HumSaveFile, 'a')
    counter = 0
    while not self.exitPr:
      hum = self.readHum()
      file.write("%2.1f" %(time.time()-startTime))
      file.write("\t")
      file.write(str(hum))
      file.write("\n")
      if hum > self.humLevel + 1:
        self.DigChannelsWithOutputByte[1][3] = 1
        self.ValveDesiredOpen = True
      elif hum < self.humLevel - 1:
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
      time.sleep(2)
      #if counter == 10:
      #  self.exitPr = True
      #counter += 1
    file.close()
    logging.info("HUMIDITY CONTROL: Ending humidity stabilization program")
    return True
    
  def readHum(self):
    f = open("{0}/humidity".format(self.humMntPath))
    humidity = float(f.readline())
    f.close()
    return humidity
    
  def firstReachHumLevel(self):
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
      while (time.time() - startTime < 60):
        currentLevel = self.readHum()
        logging.info("HUMIDITY CONTROL: Current humidity level: {0}%".format(currentLevel))
        if (currentLevel - self.humLevel) <= 0: 
          logging.info("HUMIDITY CONTROL: Humidity level sank to the desired level and will be stabilized.")
          bool = True
          break
        time.sleep(2)
      if not bool: 
        logging.warning("HUMIDITY CONTROL: Humidity level could not reach desired value. The measurements will be performed with a new humidity level of {0}%!".format(currentLevel))
        self.humLevel = currentLevel
    self.ValveCurrentlyOpen = False
    
    return True
    
  def waitForInput(self):
    print("To plot the leakage current distribution over time type 'plot'. To quit the scan please type 'exit'.")
    while not self.exitPr:
      inp = input()
      if inp == "exit":
        logging.info("USER INPUT: {0}".format(inp))
        self.exitPr = True
        #time.sleep(1)
        #self.exitProgram()
      elif inp == "plot":
        #print("Plot")
        os.system("python src/plot_LongTermTest.py {0}/{1} {2} {3} &".format(self.outputdirectory, self.DataFileName, self.InitNrScanChan, 0.001*self.limleakcurr))
      else:
        print("To plot the leakage current distribution over time type 'plot'. To quit the scan please type 'exit'.")  
  
  def checkExit(self, timetowait):
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
