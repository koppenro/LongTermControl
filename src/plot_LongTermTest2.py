import numpy as np
import matplotlib.pyplot as plt
#from scipy.odr import *
import sys
import os

if len(sys.argv) == 4:
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

  humtime = []
  humidity = []
  humidityfile = sys.argv[1][:-4]+"-Humidity.txt"
  with open(humidityfile) as g:
      for line in g:
          humtime.append( float(line.split()[0].replace(',','.'))/3600. )
          humidity.append( float(line.split()[1].replace(',','.')) )
  g.close()

  temptime = []
  temperature = []
  tempfile = sys.argv[1][:-4]+"-Temperature.txt"
  with open(tempfile) as t:
      for line in t:
          temptime.append( float(line.split()[0].replace(',','.'))/3600. )
          temperature.append( float(line.split()[1].replace(',','.')) )
  t.close()

  # Plotten
#  plt.figure(figsize=(15,9))

  # Two subplots, the axes array is 1-d
  f, axarr = plt.subplots(2, sharex=True, figsize=(15,9))
  colorplot = ['blue', 'orange', 'green', 'black', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
  for i in range(0, int(sys.argv[2])):
      axarr[0].plot(time, s[i], color=colorplot[i], label='S{0}'.format(i+1), marker='x')
  axarr[0].plot((time[0], time[-1]), (float(sys.argv[3]), float(sys.argv[3])), color='red', label='Current Limit', marker=None, linestyle='--')
  axarr[0].grid(True)
  axarr[0].legend(loc='best')
  #axarr[0].set_title('Sharing X axis')

  axarr[1].scatter(humtime, humidity, color='blue', linestyle='-', marker='.')
  axarr[1].set_ylabel('Humidity (°C)', color='blue')
  axarr[1].tick_params('y', colors='b')
  axarr[1].grid(True)
  ax2 = axarr[1].twinx()
  ax2.plot(temptime, temperature, color='red', marker=',')
  ax2.set_ylabel('Temperature (°C)', color='red')
  ax2.tick_params('y', colors='r')

  plt.savefig(sys.argv[1][:-3]+'.pdf')

  #input()

  #os.system("evince --class=test {}.pdf".format(sys.argv[1][:-4]))


#  plt.close()

else:
  print("Erstes Argument: Pfad zu Textdatei")
  print("Zweites Argument: Anzahl an Scan Channels")
  print("Drittes Argument: Grenze des Leckstroms in uA")
  #print("Falsche Benutzung!")
