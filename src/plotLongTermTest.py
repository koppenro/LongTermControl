import numpy as np
import matplotlib.pyplot as plt
import sys

"""
    Plot program for Long Term Measurements which creates graphical displays of
    leakage current data over time without using temperature or humidity data
"""


if len(sys.argv) == 4:
  with open(sys.argv[1]) as f:
    # Read in the first lines
    f.readline()
    f.readline()
    f.readline()
    f.readline()
    f.readline()

    # Define empty arrays to save data into
    time = []
    s = [[],[],[],[],[],[],[],[],[],[]]
    limleakcurr = []

    for line in f:
      time.append( float(line.split()[0].replace(',','.'))/3600. )  # convert seconds into hours
      for i in range(0,int(sys.argv[2])):
        s[i].append(1000000*float(line.split()[i+2].replace(',','.')))
      limleakcurr.append(float(sys.argv[3]))
  f.close()

  # Plotting
  plt.figure(figsize=(15,9))
  colorplot = ['blue', 'orange', 'green', 'black', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
  lim = []
  for i in range(0, int(sys.argv[2])):
    plt.plot(time, s[i], color=colorplot[i], label='S{0}'.format(i+1), marker='x')  # Plot sensor data in figure
  plt.plot((time[0], time[-1]), (float(sys.argv[3]), float(sys.argv[3])), color='red', label='Current Limit', marker=None, linestyle='--')
  plt.legend(loc='best')
  plt.xlabel("Time after scan start (h)", size=15)
  plt.ylabel("Leakage current ({0}A)".format("u"), size=15)
  plt.grid(True)
  #plt.savefig('plot_{}.png'.format(file), dpi=800)
  #plt.savefig('{}.pdf'.format(sys.argv[1][:-4]), dpi=1600)
  plt.show()

else:
  print("First argument: path to .txt file with data")
  print("Second argument: number of scan channels")
  print("Third argument: threshold of leakage current in uA")
