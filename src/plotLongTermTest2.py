import numpy as np
import matplotlib.pyplot as plt
import sys
import os

"""
    Plot program for Long Term Measurements which creates graphical displays of
    leakage current data over time and compares it with temperature and humidity
"""

if len(sys.argv) == 4:

  # Read in leakage current data
  with open(sys.argv[1]) as f:
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    f.readline()

    time = []
    s = [[],[],[],[],[],[],[],[],[],[]]
    limleakcurr = []

    for line in f:
      time.append( float(line.split()[0].replace(',','.'))/3600. )
      for i in range(0,int(sys.argv[2])):
        s[i].append(1000000*float(line.split()[i+2].replace(',','.')))
      limleakcurr.append(float(sys.argv[3]))
  f.close()

  # Read in humidity data
  humtime = []
  humidity = []
  humidityfile = sys.argv[1][:-4]+"-HumidityLog.txt"
  with open(humidityfile) as g:
      for line in g:
          humtime.append( float(line.split()[0].replace(',','.'))/3600. )
          humidity.append( float(line.split()[1].replace(',','.')) )
  g.close()

  # Read in temperature data
  temptime = []
  temperature = []
  tempfile = sys.argv[1][:-4]+"-TemperatureLog.txt"
  with open(tempfile) as t:
      for line in t:
          temptime.append( float(line.split()[0].replace(',','.'))/3600. )
          temperature.append( float(line.split()[1].replace(',','.')) )
  t.close()

  # Plotting
  f, axarr = plt.subplots(2, sharex=True, figsize=(15,9))   # Create two subplots
  colorplot = ['blue', 'orange', 'green', 'black', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
  for i in range(0, int(sys.argv[2])):
      axarr[0].plot(time, s[i], color=colorplot[i], label='S{0}'.format(i+1), marker='x')
  axarr[0].plot((time[0], time[-1]), (float(sys.argv[3]), float(sys.argv[3])), color='red', label='Current Limit', marker=None, linestyle='--')
  axarr[0].grid(True)
  axarr[0].legend(loc='best')
  axarr[0].set_ylabel('Leakage current (uA)',size=20)

  axarr[1].scatter(humtime, humidity, color='blue', linestyle='-', marker='.')
  axarr[1].set_ylabel('Humidity (%)', color='blue', size=20)
  axarr[1].tick_params('y', colors='b')
  axarr[1].grid(True)
  axarr[1].set_xlabel('Time after start (h)')
  ax2 = axarr[1].twinx()
  ax2.plot(temptime, temperature, color='red', marker=',')
  ax2.set_ylabel('Temperature (°C)', color='red',size=20)
  ax2.tick_params('y', colors='r')

  #plt.savefig(sys.argv[1][:-3]+'pdf')
  plt.show()

else:
  print("First argument: path to .txt file with data")
  print("Second argument: number of scan channels")
  print("Third argument: threshold of leakage current in uA")
