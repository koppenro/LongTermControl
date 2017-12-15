#!/usr/bin/python3

import configparser

class createDefaultCfg:

  def __init__(self):

    self.config =  configparser.ConfigParser(allow_no_value=True)

  def init(self):
    self.config['SerialPorts'] = {'Keithley2700':'/dev/ttyUSB0',
                                  'ISEGT2DP': '/dev/ttyUSB1'}

    self.config.add_section('Sensors')
    self.config.set('Sensors', 'LimLeakCurr', '250')
    self.config.set('Sensors', 'SensorLabel1', 'S1')
    self.config.set('Sensors', 'SensorLabel2', 'S2')
    self.config.set('Sensors', 'SensorLabel3', 'S3')
    self.config.set('Sensors', 'SensorLabel4', 'S4')
    self.config.set('Sensors', 'SensorLabel5', 'S5')
    self.config.set('Sensors', 'SensorLabel6', 'S6')
    self.config.set('Sensors', 'SensorLabel7', 'S7')
    self.config.set('Sensors', 'SensorLabel8', 'S8')
    self.config.set('Sensors', 'SensorLabel9', 'S9')
    self.config.set('Sensors', 'SensorLabel10', 'S10')

    self.config.set('Sensors', '#LimLeakCurr: Limit for allowed leakage current in nA', None)
    #self.config.set('Sensors', '#SensorLabelX: label of sensor', None)

    self.config.add_section('DCVoltageScan')
    self.config.set('DCVoltageScan', 'VoltChannel', '2')
    self.config.set('DCVoltageScan', 'DCVoltage', '300')
    self.config.set('DCVoltageScan', 'Polarity', '-')
    self.config.set('DCVoltageScan', 'ScanChannels', '201:210')
    self.config.set('DCVoltageScan', 'VoltageRange','auto')
    self.config.set('DCVoltageScan', 'tbm', '30')
    self.config.set('DCVoltageScan', 'writeeachtrigger', '5')
    self.config.set('DCVoltageScan', 'maxtime', '72')

    self.config.set('DCVoltageScan', '#VoltChannel: Channel of iseg to be used (1 or 2)', None)
    self.config.set('DCVoltageScan', '#DCVoltage: DC voltage in V', None)
    self.config.set('DCVoltageScan', '#ScanChannels: "101:110" for scanning channel 101 to 110 or list of channels "101,103,102"', None)
    self.config.set('DCVoltageScan', '#VoltageRange: Possible voltage ranges are {.1, 1, 10, 100, 1000} V', None)
    self.config.set('DCVoltageScan', '#tbm: Time in seconds between two trigger signals', None)
    self.config.set('DCVoltageScan', '#writeeachtrigger: Rate of writing results into external file. "n" for saving results every n measurement', None)
    self.config.set('DCVoltageScan', '#maxtime: maximum time of scan after which program will end in hours', None)

    #self.config.add_section('IVCurves')
    #self.config.set('IVCurves', 'Enable', '0')
    #self.config.set('IVCurves', 'VoltageSteps', '5')
    #self.config.set('IVCurves', 'scaneachtrigger', '2')
    #self.config.set('IVCurves', '#Enable: Enable IV curve measurements during scan', None)
    #self.config.set('IVCurves', '#scaneachtrigger: rate for performing IV curve measurements. "n" for scanning each trigger event of DC voltage scan', None)

    self.config.add_section('HumidityReadout')
    self.config.set('HumidityReadout', 'humlevel', '20')
    self.config.set('HumidityReadout', 'mntpath', '/dev/1-wire/honeywell')

    with open('LongTermTestControl.cfg', 'w') as configfile:
      self.config.write(configfile)
    print("Created default config file LongTermTestControl.cfg")

# main loop
if __name__=='__main__':

  c = createDefaultCfg()
  c.init()
