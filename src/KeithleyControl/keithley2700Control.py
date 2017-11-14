#!/usr/bin/python3

import sys, time, math
from serial import *
import logging

class keithley2700:
  
  def __init__(self, SerialPort=None, logBool = False):
    
    self.baudrate=9600
    self.bytesize=8
    self.xonxoff=True
    self.logBool = logBool
    if SerialPort == None:
      self.port = "/dev/ttyUSB0"
    else:
      self.port=SerialPort
    
  def init(self):
    """initialize connection to Keithley2700
    
      Raises: 
        * Value Error if serial port could not be opened
      Returns: 
        * True if everything worked fine
        
        
      TODO: FALLS KEITHLEY NICHT ANTWORTET WEIL PORT NICHT RICHTIG ZEITABSCHALTUNG MIT FEHLERMELDUNG HINZUFUEGEN
    """
    
    try:
      #
      #Open port
      #
      #Syntax: serial.Serial(port=None, baudrate=9600, bytesize=EIGHTBITS, parity=PARITY_NONE,
      #                      stopbits=STOPBITS_ONE, timeout=None, xonxoff=False, rtscts=False,
      #                      writeTimeout=None, dsrdtr=False, interCharTimeout=None)
      self.port = Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize, xonxoff=self.xonxoff)
      self.printout("Opening serial port to Keithley 2700", "info")
      
  #NOCH ZU TESTEN!!!
#      self.port.write("STAT:OPER:ENAB?")  #S. 304 im Handbuch 2700
#      line = self.port.readline()
#      print line 
      
    except:
      self.printout("ValueError! Keithley 2700 port is already claimed or can not be found!", "error")
      raise ValueError("Keithley 2700 port is already claimed or can not be found!")
	
		# Custom settings
    # Reset Keithley
    self.port.write("*RST\r\n".encode())
    # Disable hardware beeper
    self.port.write(":SYST:BEEP OFF\r\n".encode())
    self.printout("Serial port to Keithley 2700 opened", "info")
    
    return True
  
  def checkRange(self, keyword, Range):
    """check if choice of range is compatible with Keithley standard 
    
      Args:
        * str keyword: keyword for measurement type: 'DCV', 'ACV', 'DCI' and 'ACI' possible
        * int Range: desired range value to be checked
        
      Returns:
        * boolean
    """
    
    if (keyword == 'DCV'):
      allowedRange=[.1, 1, 10, 100, 1000]	#allowed DC voltage ranges in V
    elif (keyword == 'ACV'):
      allowedRange=[.1, 1, 10, 100, 750]	#allowed AC voltage ranges in V
    elif (keyword == 'DCI'):
      allowedRange=[.02, .1, 1, 3]	#allowed DC current ranges in A
    elif (keyword == 'ACI'):
      allowedRange=[1, 3]	#allowed AC current ranges in A
    
    if Range == 'auto':
      return True  
    for i in allowedRange:
      if float(Range) == float(i): 
        return True
    
    if (keyword == 'DCV'):
      self.printout("Wrong DC voltage range. Allowed values are .1, 1, 10, 100 or 1000 (in V)", "error")
    elif (keyword == 'ACV'):
      self.printout("Wrong AC voltage range. Allowed values are .1, 1, 10, 100 or 750 (in V)", "error")
    elif (keyword == 'DCI'):
      self.printout("Wrong DC current range. Allowed values are .02, .1, 1 or 3 (in A)")
    elif (keyword == 'ACI'):
      self.printout("Wrong AC current range. Allowed values are 1 or 3 (in A)", "error")
    return False
  
  
  def setRange(self, keyword, Range='auto'):
    """set DC/AC voltage/current range
        
      Args: 
        * str keyword: 'DCV', 'ACV', 'DCI' or 'ACI' to define measurement
        * int Range: desired range ('auto' or float numbers)
      Returns: 
        * boolean 
    """
    
    if (not self.isFloat(Range) and Range != "auto"):   #avoid letter input besides 'auto'
      self.printout("Wrong input format, only float numbers or 'auto' allowed for range", "error")
      return False
    else:
      if (self.checkRange(keyword, Range)):
        if (keyword == "DCV"):
          if (Range == "auto"):
            self.port.write("VOLT:DC:RANG:AUTO ON\r\n".encode())
          else :
            self.port.write(("VOLT:DC:RANG %s\r\n" %(Range)).encode())
          return True
        elif (keyword == "ACV"):
          if (Range == "auto"):
            self.port.write("VOLT:AC:RANG:AUTO ON\r\n")
          else:
            self.port.write(("VOLT:AC:RANG %s\r\n" %(Range)).encode())
          return True
        elif (keyword == "DCI"):
          if (Range == "auto"):
            self.port.write("CURR:DC:RANG:AUTO ON\r\n")
          else:
            self.port.write(("CURR:DC:RANG %s\r\n" %(Range)).encode())
          return True
        elif (keyword == "ACI"):
          if (Range == "auto"):
            self.port.write("CURR:AC:RANG:AUTO ON\r\n".encode())
          else:
            self.port.write(("CURR:AC:RANG %s\r\n" %(Range)).encode())
          return True
        else :
          self.printout("Please check the keyword! Allowed keywords are 'DCV', 'ACV', 'DCI' and 'ACI'", "error")
          return False
      else:
        return False
  
  
  def measure(self, keyword, Range='auto', nrChannel=None):
    """measure DC/AC voltage/current
        
      Args: 
        * str keyword: 'DCV', 'ACV', 'DCI' or 'ACI' to define measurement
        * int Range: desired range ('auto' or float numbers)
        * int nrChannel: analog channel of 7707 multiplexer card to be closed (None means measurement at front inputs of Keithley2700) 
      Returns: 
        * float meas: Measurements in chosen channel
    """
    
    #Check if range is reasonable
    if(self.checkRange(keyword, Range)):
      if (keyword == "DCV"):
        self.port.write("FUNC 'VOLT:DC'\r\n".encode())
      elif (keyword == "ACV"):
        self.port.write("FUNC 'VOLT:AC'\r\n".encode())
      elif (keyword == "DCI"):
        self.port.write("FUNC 'CURR:DC'\r\n".encode())
      elif (keyword == "ACI"):
        self.port.write("FUNC 'CURR:AC'\r\n".encode())
      
      #Close channel if wanted (only possible for voltage measurements!
      if (keyword == "DCV" or keyword == "ACV"):
        if (nrChannel != None):
          self.closeAnalogChannel(nrChannel)
      elif (keyword == "DCI" or keyword == "ACI"):
        if (nrChannel != None):
          self.printout("WARNING: Keithley 7707 Multiplexer cards supports no current measurements in analog channels! No channel will be closed!", "warning")
      
      #Trigger and readout measurement
      self.port.write("READ?\r\n".encode())
      line = self.port.readline()
      print ("readline ", line)
      splitted = line.split(",")
      return splitted[0][1:-3] #cut off "VDC"/"VAC"/"ADC"/"AAC" at the end 
    else:
      self.printout("No measurement will be done! Please try again and check your settings!", "warning")
      return None

  
  def closeAnalogChannel(self, NrChannel):
    """Close analog channel of 7707 multiplexer card
        
      Args: 
        * int NrChannel: number of analog channel of 7707 multiplexer card to close and enable measurements
    """
    
    # Number of possible Channels depend on inserted Cards in slots
    # For 7707 Multiplexer-Digital I/O Module in slot 1:
    #   Channel 101 to 110: analog system measurement channels (no current measurement!)
    self.port.write("ROUT:CLOS (@%s)\r\n" %(NrChannel).encode())

    
  def setDigitalIOChannel(self, NrChannel, Output=False):
    """Define status of digital I/O channels on 7707 multiplexer card
    
      Args: 
        * int NrChannel: number of digital I/O channel to set as I/O
        * Output: status to set channel, true means channel will be set as output channel
        
      Keithley 7707 multiplexer card provides four digital I/O channels to be set as input or output ports: 111, 112, 113 and 114. 
    """
    
    #Syntax: set channels 111 to 113 as output: NrChannel = "111:113" and Output=True
    if Output:
      self.port.write(("OUTP:DIG:STAT 1, (@%s)\r\n" %(NrChannel)).encode())  # 1 = output port
    else:
      self.port.write(("OUTP:DIG:STAT 0, (@%s)\r\n" %(NrChannel)).encode())  # 0 = input port
    
    #Read configuration status of all four digital channels
    self.port.write(("OUTP:DIG:STAT? (@%s)\r\n" %(NrChannel)).encode())
    line = str(self.port.readline().decode())
    line = line.replace('\r', '')
    self.printout("Status of digital output channel (%s): (%s)" %(NrChannel, line[:-1]), "info")

    
  def setDigitalOutputByte(self, NrChannel, binaryAddress, boolLog=True):
    """Set status of bits in output channel using bytes
      
      Args
        * int NrChannel: number of digital output channel 
        * str binaryAddress: binary pattern of states of output channel, e.g. '10011010'
    """
    
    #Set output format for reading of byte settings in channel to binary
    self.port.write("OUTP:DIG:FORM BIN, 8\r\n".encode())   # ASC for decimal
    
    #Set configuration status of bytes in channel
    self.port.write(("OUTP:DIG:BYTE #B%s, (@%s)\r\n" %(binaryAddress, NrChannel)).encode())
    #Read configuration status of bytes in channel
    self.port.write(("OUTP:DIG:BYTE? (@%s)\r\n" %(NrChannel)).encode())
    line = str(self.port.readline())
    if boolLog:
      self.printout("Binary status of digital output lines in channels @%s: %s" %(NrChannel, line[6:-3]), "info")
    

  def initDCVoltScan(self, NrScannedChannels=10, NrChannels="101:110", VolRange='auto', DigChannelsWithOutputByte=None):
    """initialize DC voltage scan with 7707 multiplexer card
    
      Args:
        * int NrScannedChannels: number of channels to be scanned
        * str NrChannels: name of channels to be scanned (e.g. '101:110' or '101,102,107,103')
        * int VolRange: desired voltage range value
        * str NrDigChannels: name of digital channels to set as output channel (e.g. '111:114' or '111,113')
        
      Returns:
        * boolean
    """
    
    #Set digital outputs to control relay
    if (DigChannelsWithOutputByte != None):
      self.setDigitalIOChannel("{0}:{1}".format(DigChannelsWithOutputByte[0][0], DigChannelsWithOutputByte[1][0]), True)
      binPattern = ""
      for i in (DigChannelsWithOutputByte[0][::-1]):
        if (int(i) < 99):
          binPattern += str(i)
      self.setDigitalOutputByte(DigChannelsWithOutputByte[0][0], binPattern)
      
      binPattern = ""
      for i in (DigChannelsWithOutputByte[1][::-1]):
        if (int(i) < 99):
          binPattern += str(i)
      self.setDigitalOutputByte(DigChannelsWithOutputByte[1][0], binPattern)
    
    #init DC Voltage scan with analog channels
    if self.checkRange('DCV', VolRange):
      self.port.write("TRAC:CLE\r\n".encode()) # Clear buffer
      self.port.write("INIT:CONT OFF\r\n".encode())  #Disable continuos initiation
      self.port.write("TRIG:SOUR IMM\r\n".encode())  #Select immediate control source
      self.port.write("TRIG:COUN 1\r\n".encode())  #Perform one scan
      self.port.write(("SAMP:COUN %s \r\n" %(NrScannedChannels)).encode())  #Scan 10 channels of scan list
      self.port.write(("SENS:FUNC 'VOLT', (@%s)\r\n" %(NrChannels)).encode()) #Define scan function in channels
      if VolRange == 'auto':
        self.port.write(("VOLT:DC:RANG:AUTO ON, (@%s)\r\n" %(NrChannels)).encode())
      else:
        self.port.write(("VOLT:DC:RANG %s, (@%s)\r\n" %(VolRange, NrChannels)).encode())  #Set Voltage range
      self.port.write(("ROUT:SCAN (@%s)\r\n" %(NrChannels)).encode()) #Create scan list with channels
      self.port.write("ROUT:SCAN?\r\n".encode())
      line = self.port.readline()
      if VolRange == 'auto':
        self.printout("When triggered, scan will be measuring DC voltage with automatic range in %s channels: @%s" %(NrScannedChannels, NrChannels), "info")
      else:
        self.printout("When triggered, scan will be measuring DC voltage with a range of %sV in %s channels: @%s" %(VolRange, NrScannedChannels, NrChannels), "info")
      self.port.write("ROUT:SCAN:TSO IMM\r\n".encode())  #Start scan when enabled and triggered
      self.port.write("ROUT:SCAN:LSEL INT\r\n".encode()) #Enable scan
      return True
    else:
      return False

    
  def trigDCVoltScan(self, NrScannedChannels=10, R=400):
    """trigger DC voltage scan after it was initialized to perform one scan cycle and return the measured data 
    
      Args:
        * int NrScannedChannels: number of channels to be scanned
        * float R: resistance in kOhm
        
      Returns:
        * float[] DCVoltages: list of measured values of all scanned channels in same order as scan
    """
    
    R = 400 # R in kOhm
    self.port.write("READ?\r\n".encode())
    line = str(self.port.readline())
    line = line[4:-1]
    #Pick out voltage values and convert to float
    splitted = line.split(',')
    DCVoltages = []
    DCCurrents = []
    for i in range(0,NrScannedChannels):
      DCVoltages.append(abs(float(splitted[3*i][0:-3])))
      DCCurrents.append(abs(float(splitted[3*i][0:-3])/(1000.*R)))
    self.printout("Measurement triggered.", "info")
    #self.printout(DCVoltages, "info")
    self.printout("Measured DC currents: ", "info")
    self.printout(DCCurrents, "info")
    return DCVoltages, DCCurrents

  
  def reset(self):
    """reset Keithley2700
    """
    
    #Clear all error messages
    self.port.write("*CLS\r\n".encode())
    #Reset Keithley
    self.port.write("*RST\r\n".encode())
    #Load Presettings 
    self.port.write("STAT:PRES\r\n".encode())
    #Init custom settings
    self.port.write(":SYST:BEEP OFF\r\n".encode())
  
  
  def close(self):
    """reset Keithley2700 and close serial connection
    """
    
    #Reset Keithley
    self.port.write("*RST\r\n".encode())
    #Clear all error messages
    self.port.write("*CLS\r\n".encode())
    #Load Presettings 
    self.port.write("STAT:PRES\r\n".encode())
    # Set "LOCAL" mode
    self.port.write(":SYST:KEY 17\r\n".encode())
    #Close connection
    self.port.close()

#TODO: Loesche Funktion nach Debuggen!!!    
  def installPseudoCard(self):
    self.port.write("SYST:PCAR2 C7707\r\n".encode())
  
    
  def isFloat(self, string):
    """check if a string can be converted to a float number
    
      Args:
        * str string
        
      Returns:
        * boolean
    """

    try:
        float(string)
        return True
    except ValueError:
        return False
        
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

    
# main loop
if __name__=='__main__':

    # Instanciate Keithly
    k = keithley2700("COM3")
    
    k.init()
    #k.installPseudoCard()
    #k.setRange("DCV", "auto")
    
    # k.initDCVoltScan(10, "101:110", "auto")
    #k.trigDCVoltScan(10)
    
    k.setDigitalIOChannel("111:114", True)
    k.setDigitalOutputByte("111", "00001000")
    k.setDigitalOutputByte("112", "00000000")
    input()
    k.setDigitalOutputByte("111", "00000000")
    #k.setDigitalOutputByte("111", "00000000")
    
    #4
    
    #time.sleep(2)
    #k.setDigitalOutputByte("212", "00000100")
    #time.sleep(2)
    #k.setDigitalOutputByte("212", "00000000")
    #print("test2")
    #k.setDigitalOutputByte("211", "00000010")
    #print("test2")
    
    #k.setDigitalIOChannel("111:114", True)
    #time.sleep(3)
    #k.setDigitalIOChannel("111:114", True)
    #k.setDigitalOutputByte("112", "00000000")
#    k.setDigitalOutputByte("112", "00001101")
#    k.initiateDCVoltageScan(9, "201:209", VolRange=10)
#    k.triggerDCVoltageScan(9)
#    time.sleep(5)
#    k.triggerDCVoltageScan(9)
#    time.sleep(5)
#    k.triggerDCVoltageScan(9)
#    time.sleep(5)
#    k.triggerDCVoltageScan(9)
#    time.sleep(5)
#    k.triggerDCVoltageScan(9)
#    k.reset()

    
  
