#!/usr/bin/python3

import sys, time, math
import serial
import logging

class isegT2DP:
  
  
  def __init__(self, port = None, logBool = False):
    
    if port == None:
        self.port = "/dev/ttyUSB0"
    else:
        self.port = port

    self.baudrate = 9600
    self.bytesize = serial.EIGHTBITS
    self.parity = serial.PARITY_NONE
    self.stopbits = serial.STOPBITS_ONE
    self.timeout = 0.25
    self.xonxoff = True
    self.communicative = True
    self.logBool = logBool
  
    
  def init(self):

    try:
      #Open port
      #Syntax: serial.Serial(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE,
      #                      stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False,
      #                      writeTimeout=None, dsrdtr=False, interCharTimeout=None)
      self.printout("Opening serial port to Iseg T2DP", "info")
      self.ser = serial.Serial(port=self.port,
                               baudrate=self.baudrate,
                               bytesize=self.bytesize,
                               parity=self.parity,
                               stopbits=self.stopbits,
                               timeout=self.timeout)
      #self.ser.write("\r\n")
        
  
    except:
      self.printout("Iseg T2DP port is already claimed or can not be found!", "error")
      raise ValueError("Iseg T2DP port is already claimed or can not be found!")
    
    self.printout("Serial port to Iseg T2DP opened", "info")
    return True
      
  
  def getIDN(self, nrChannel=1):
    self.checkChannel(nrChannel)

    self.send_iseg("#%s" %(nrChannel))
    answer = self.read_iseg(28).replace("\r\n","")
    if (nrChannel == 1):
      if self.communicative:
        self.printout("#1 %s" %(answer[3:-1]), "info")
      return answer[3:-1]
    else:
      if self.communicative:
        self.printout("#2 %s" %(answer[1:-1]), "info")
      return answer[1:-1]
    
  
  def getVoltage(self, nrChannel=1, printout = True):
    self.checkChannel(nrChannel)
    
    self.send_iseg("U%s" %(nrChannel))
    answer = self.read_iseg(10).replace("\r\n","")
    if (nrChannel == 1):  
      if self.communicative and printout:
        self.printout("Current CH%s voltage is U%s = %s V" %(nrChannel, nrChannel, answer[3:-1]), "info")
      return float(answer[3:-1])
    else:
      if self.communicative and printout:
        self.printout("Current CH%s voltage is U%s = %s V" %(nrChannel, nrChannel, answer[1:-1]), "info")
      return float(answer[1:-1])

      
  def getCurrent(self, nrChannel=1):
    self.checkChannel(nrChannel)

    self.send_iseg("I%s" %(nrChannel))
    answer = self.read_iseg(15).replace("\r\n","")
    if (nrChannel == 1):
      if self.communicative:
        self.printout("Current CH%s current is I%s = %s A" %(nrChannel, nrChannel, answer[3:-1]), "info")
      return float(answer[3:-1])
    else:
      if self.communicative:
        self.printout("Current CH%s current is I%s = %s A" %(nrChannel, nrChannel, answer[1:-1]), "info")
      return float(answer[1:-1])


  def getPolarity(self, nrChannel=1):
    self.checkChannel(nrChannel)

    self.send_iseg("P%s" %(nrChannel))
    answer = self.read_iseg(15).replace("\r\n","")
    if (nrChannel == 1):
      if self.communicative:
        self.printout("Polarity setting of CH%s is P%s = %s" %(nrChannel, nrChannel, answer[3:-1]), "info")
      return answer[3:-1]
    else:
      if self.communicative:
        self.printout("Polarity setting of CH%s is P%s = %s" %(nrChannel, nrChannel, answer[1:-1]), "info")
      return answer[1:-1]

  def setVoltage(self, nrChannel=1, val=0, tsleep = 5):
    self.checkChannel(nrChannel)

    try:
      val = int(val)
      if val<0:
        val = abs(val)
      else:
        pass
    except:
      self.printout("Invalid voltage input.", "error")
      raise ValueError("Invalid voltage input.")
  
    self.send_iseg("D%s=%s" %(nrChannel, str(val)))
    answer = self.read_iseg(10)
    if (nrChannel == 1):
      if self.communicative:
        string = "CH%s voltage will be set to U%s = %sV. Please wait a moment!" %(nrChannel, nrChannel, answer[3:])
        self.printout(string, "info")
    else:
      if self.communicative:
        string = "CH%s voltage will be set to U%s = %sV. Please wait a moment!" %(nrChannel, nrChannel, answer[1:])
        self.printout(string, "info")
    
    while True:
      time.sleep(tsleep)
      currentVoltage = self.getVoltage(nrChannel, False)
      if currentVoltage >= val-2.5:
        self.printout("CH%s voltage has reached %s V." %(nrChannel, val), "info")
        break
      else:
        self.printout("CH%s voltage was not yet reached (currently at %s V). Please wait a moment!" %(nrChannel, currentVoltage), "warning")
  
    return True
    
  
  def setCurrent(self, nrChannel=1, val=0, tsleep = 5):
    self.checkChannel(nrChannel)

    #try:
    #  val = int(val)
    #  if val<0:
    #    val = abs(val)
    #  else:
    #    pass
    #except:
    #  self.printout("Invalid current input.", "error")
    #  raise ValueError("Invalid current input.")
  
    print("C%s=%s" %(nrChannel, str(val)))
    self.send_iseg("C%s=%s" %(nrChannel, str(val)))
    answer = self.read_iseg(10)
    if (nrChannel == 1):
      if self.communicative:
        string = "CH%s current will be set to I%s = %sA. Please wait a moment!" %(nrChannel, nrChannel, answer[3:])
        self.printout(string, "info")
    else:
      if self.communicative:
        string = "CH%s current will be set to I%s = %sA. Please wait a moment!" %(nrChannel, nrChannel, answer[1:])
        self.printout(string, "info")
    
    while True:
      time.sleep(tsleep)
      currentCurrent = self.getCurrent(nrChannel)
      if currentCurrent >= val-0.1:
        break
      else:
        self.printout("CH%s current was not yet reached (currently at %sA). Please wait a moment!" %(nrChannel, currentCurrent), "warning")
  
    return True


  def setPolarity(self, nrChannel=1, val="-"):
    self.checkChannel(nrChannel)

    if val != "+" and val != "-":
      self.printout("Invalid polarity input.", "error")
      raise ValueError("Invalid polarity input.")
    else:
      pass
  
    self.send_iseg("P%s=%s" %(nrChannel, str(val)))
    answer = self.read_iseg(10)
    if (nrChannel == 1):
      if self.communicative:
        self.printout("CH%s polarity will be set to P%s = %s. Please wait a moment" %(nrChannel, nrChannel, answer[3:]), "info")
    else:
      if self.communicative:
        self.printout("CH%s polarity will be set to P%s = %s. Please wait a moment" %(nrChannel, nrChannel, answer[1:]), "info")
      
    while True:
      time.sleep(3)
      currentPolarity = self.getPolarity(nrChannel)
      if currentPolarity == str(val):
        break
      else:
        self.printout("CH%s polarity was not yet set. Please wait a moment!" %(nrChannel), "warning")
        
    #print "CH%s polarity is set to P%s = %s" %(nrChannel, nrChannel, answer[3:])
  
    return True
        
    
  def send_iseg(self, cmd):

    for c in cmd + "\r\n":
      self.ser.write(c.encode("utf-8"))
      echo = self.ser.read(2)
    
    return True
  
    
  def read_iseg(self, n):

    answer = self.ser.read(n).decode("utf-8").replace("\r\n"," ")
  
    return answer
  
  
  def checkChannel(self, nrChannel):
    if nrChannel != 1 and nrChannel != 2:
      self.printout("Invalid channel input.", "error")
      raise ValueError("Invalid channel input.")
    else:
      pass
    return True
    
  def VoltageShutdown(self, nrChannel):
    self.checkChannel(nrChannel)
    
    self.printout("CH%s voltage will be shut down!" %(nrChannel), "info")
    self.setVoltage(nrChannel, 0, 25)
    
  def printout(self, string, logKeyword):
    if self.logBool:
      if logKeyword == "error":
        logging.error(string)
      elif logKeyword == "info":
        logging.info(string)
      elif logKeyword == "warning":
        logging.warning(string)
      elif logKeyword == "debug":
        logging.debug(string)
    else:
      print(string)
      
  def setVoltageToZero(self, nrChannel):
    self.checkChannel(nrChannel)
    
    
# main loop
if __name__=='__main__':

  i = isegT2DP("/dev/ttyUSB0")
  i.init()
  i.getIDN(2)
  #i.test(30)
  #i.getIDN(2)
  i.getVoltage(2)
  #i.getCurrent(2)
  #i.getPolarity()
  i.setVoltage(2, 100)
  #i.setPolarity(1, "-")
  #i.setPolarity(2, "+")
  #i.setVoltage(2, 30)
  #i.setCurrent(2,1)
  #i.VoltageShutdown(2)
