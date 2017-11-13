#!/usr/bin/python3

import numpy as np
import matplotlib.pyplot as plt
import sys
import os

class RKPlot:

  #def __init__(self):
    
    #self.time = []
    #self.voltage = []
    #self.scurrent = [[],[],[],[],[],[],[],[],[],[]]
    #self.limleakcurr = []
  
  
  def readin(self, pathtofile, nrcolumns = 12, nrcomments = 4, printout = False):
    with open(pathtofile) as f:
      for i in range(0,nrcomments):
        f.readline()
      readinVector = [[],[],[],[],[],[],[],[],[],[],[],[]]
      for line in f:
        for i in range(0,nrcolumns):
          readinVector[i].append(float(line.split()[i].replace(',','.')))
          if printout:
            print(readinVector[i])
      return readinVector
      
      
          
  def plot(self, plotVector):
    colorplot = ['blue', 'orange', 'green', 'black', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
    plt.figure(figsize=(15,10))
    #if error:
      #plt.errorbar(x_value, y_value, xerr=x_error, yerr=y_error, linestyle='None', marker='o', color='black', markersize=5, label='Messwerte')
      #plt.errorbar(self.time, self.scurrent[i])
    for i in range(0, 10):
      plt.plot(self.time, self.scurrent[i], color=colorplot[i], label='s{0}'.format(i), marker='x')
    plt.legend(loc='lower left')
    #plt.title(title, size=20) 
    plt.xlabel("Time after scan start (s)", size=15)
    plt.ylabel("Leakage current (uA)", size=15)
    plt.grid(True)
    #plt.savefig('plot_{}.png'.format(file), dpi=800)
    #plt.savefig('{}.pdf'.format(sys.argv[1][:-4]), dpi=1600)
    plt.show()

# main loop
if __name__=='__main__':
    
    p = RKPlot()
    Scan10 = p.readin("output/LongTermScan-2017_11_06-11_24_34.txt")
    Scan1 = p.readin("output/LongTermScan-2017_11_06-11_15_39.txt", 3)
    Scan10_2 = p.readin("output/LongTermScan-2017_11_06-11_39_43.txt")
    Scan1_2 = p.readin("output/LongTermScan-2017_11_06-11_55_30.txt", 3)
    Scan1_3 = p.readin("output/LongTermScan-2017_11_06-13_28_24.txt", 3)
    Scan1_4 = p.readin("output/LongTermScan-2017_11_06-13_32_57.txt", 3)
    Scan1_5 = p.readin("output/LongTermScan-2017_11_06-13_43_26.txt", 3)
    Scan1_6 = p.readin("output/LongTermScan-2017_11_06-14_05_07.txt", 3)
    Scan1_7 = p.readin("output/LongTermScan-2017_11_06-14_19_08.txt", 3)
    Scan1_8 = p.readin("output/LongTermScan-2017_11_06-14_29_43.txt", 3)
    
    x_err = [0]*len(Scan1[0])
    y_err = [0.000001]*len(Scan1[0])
    
    for i in range(0,len(Scan10[0])):
      Scan10[2][i] = 1000*400*Scan10[2][i]
    for i in range(0, len(Scan1[0])):
      Scan1[2][i] = 1000*400*Scan1[2][i]
    for i in range(0, len(Scan10_2[0])):
      Scan10_2[2][i] = 1000*400*Scan10_2[2][i]
    for i in range(0, len(Scan1_2[0])):
      Scan1_2[2][i] = 1000*400*Scan1_2[2][i]
    for i in range(0, len(Scan1_3[0])):
      Scan1_3[2][i] = 1000*400*Scan1_3[2][i]
    for i in range(0, len(Scan1_4[0])):
      Scan1_4[2][i] = 1000*400*Scan1_4[2][i]
    for i in range(0, len(Scan1_5[0])):
      Scan1_5[2][i] = 1000*400*Scan1_5[2][i]
    for i in range(0, len(Scan1_6[0])):
      Scan1_6[2][i] = 1000*400*Scan1_6[2][i]
    for i in range(0, len(Scan1_7[0])):
      Scan1_7[2][i] = 1000*400*Scan1_7[2][i]
    for i in range(0, len(Scan1_8[0])):
      Scan1_8[2][i] = 1000*400*Scan1_8[2][i]
    
    plt.figure(figsize=(15,10))
    plt.errorbar(Scan1[0], Scan1[2], xerr = x_err, yerr = y_err, linestyle='None', color='red', label='First1ChannelScan', marker='x')
    plt.plot(Scan10[0], Scan10[2], '-', color='blue', label='Second10ChannelScan', marker='x')
    plt.plot(Scan10_2[0], Scan10_2[2], '-', color='green', label='Third10ChannelScan', marker='x')
    plt.plot(Scan1_2[0], Scan1_2[2], '-', color='orange', label='Fourth1ChannelScan', marker='x')
    plt.plot(Scan1_3[0], Scan1_3[2], '-', color='purple', label='Fifth1ChannelScan', marker='x')
    #plt.plot(Scan1_4[0], Scan1_4[2], '-', color='brown', label='Sixth1ChannelScan-100V', marker='x')
    #plt.plot(Scan1_5[0], Scan1_5[2], '-', color='olive', label='Seventh1ChannelScan-100V-keine_Erdung', marker='x')
    #plt.plot(Scan1_6[0], Scan1_6[2], '-', color='cyan', label='Seventh1ChannelScan-300V-Keithley', marker='x')
    plt.plot(Scan1_7[0], Scan1_7[2], '-', color='cyan', label='Seventh1ChannelScan-300V-KabelCh2', marker='x')
    plt.plot(Scan1_8[0], Scan1_8[2], '-', color='brown', label='Seventh1ChannelScan-300V-KabelCh2-mitWartezeitvorErsterMessung', marker='x')
    
    
    
    plt.xlabel("Time after scan start (s)", size=15)
    plt.ylabel("Voltage at 400kOhm (V)", size=15)
    
    plt.legend(loc='upper right')
    
    plt.grid(True)
    plt.show()