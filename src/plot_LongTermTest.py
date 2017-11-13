import numpy as np
import matplotlib.pyplot as plt
#from scipy.odr import *
import sys
import os


#################################################################################
# Schreibe in die filelist alle Textdateien rein, die ausgelesen werden sollen. #
# Lass jeweils '.txt' weg, setze den restlichen Namen in ''                     #
# und trenne verschiedene Textdateien mit Komma.                                #
#################################################################################

filelist = ['testdata3']

if len(sys.argv) == 4:
  with open(sys.argv[1]) as f:
    # Einlesen der Daten aus der Textdatei
    f.readline()				# Liest erste Zeile des Textdokuments, speichert sie nirgends (beinhaltet nur Erklaerungen)
    #title = f.readline().replace('\r\n','')	# Liest zweite Zeile, speichert den Titel
    f.readline()				# Liest dritte Zeile des Textdokuments, speichert sie nirgends
    #x_name = f.readline().replace('\r\n','')# Liest vierte Zeile, speichert x-Achsenbeschriftung
    f.readline()
    f.readline()
    #y_name = f.readline().replace('\r\n','')
    #f.readline()
    
    #time, s1, s2, s3, s4, s5, s6, s7, s8, s9, s10 = [],[],[],[],[],[],[],[],[],[],[]  # Definiert leere arrays
    time = []
    s = [[],[],[],[],[],[],[],[],[],[]]
    limleakcurr = []
    for line in f: #liest 4 Zahlen pro Zeile, ersetzt Komma durch Punkt, sofern vorhanden.
      time.append( float(line.split()[0].replace(',','.')) )
      #s[0].append( float(line.split()[1].replace(',','.')))
      for i in range(0,int(sys.argv[2])):
        s[i].append(1000000*float(line.split()[i+2].replace(',','.')))
        #s1.append( float(line.split()[1].replace(',','.')) )
        #s2.append( float(line.split()[2].replace(',','.')) )
        #s3.append( float(line.split()[3].replace(',','.')) )
        #s4.append( float(line.split()[4].replace(',','.')) )
        #s5.append( float(line.split()[5].replace(',','.')) )
        #s6.append( float(line.split()[6].replace(',','.')) )
        #s7.append( float(line.split()[7].replace(',','.')) )
        #s8.append( float(line.split()[8].replace(',','.')) )
        #s9.append( float(line.split()[9].replace(',','.')) )
        #s10.append( float(line.split()[10].replace(',','.')) )
      limleakcurr.append(float(sys.argv[3]))
  
  f.close()
  
  # Plotten
  plt.figure(figsize=(15,10))
  #plt.errorbar(x_value, y_value, xerr=x_error, yerr=y_error, linestyle='None', marker='o', color='black', markersize=5, label='Messwerte')
  #fitlabel='Lineare Regression \n $ y= m \cdot x +c$ \n $m= {} \pm {}$ \n $c= {} \pm {}$'.format(str(m),str(m_error),str(c),str(c_error))
  colorplot = ['blue', 'orange', 'green', 'black', 'purple', 'brown', 'pink', 'gray', 'olive', 'cyan']
  lim = []
  for i in range(0, int(sys.argv[2])):
    plt.plot(time, s[i], color=colorplot[i], label='S{0}'.format(i+1), marker='x')
  #plt.plot(time, lim, 'go-', label='line 1', linewidth=2)
  plt.plot((time[0], time[-1]), (float(sys.argv[3]), float(sys.argv[3])), color='red', label='Current Limit', marker=None, linestyle='--')
  #plt.plot(time, limleakcurr, color='red', label='Leakage current limit = {0}uA'.format(float(sys.argv[3])), linestyle='--')
  #plt.plot(time, s[0], color='blue', label='s1')
#  plt.plot(time, s1, color='blue', label='s1')
#  plt.plot(time, s2, color='orange', label='s2')
#  plt.plot(time, s3, color='green', label='s3')
#  plt.plot(time, s4, color='red', label='s4')
#  plt.plot(time, s5, color='purple', label='s5')
#  plt.plot(time, s6, color='brown', label='s6')
#  plt.plot(time, s7, color='pink', label='s7')
#  plt.plot(time, s8, color='gray', label='s8')
#  plt.plot(time, s9, color='olive', label='s9')
#  plt.plot(time, s10, color='cyan', label='s10')
  plt.legend(loc='best')
  #plt.title(title, size=20) 
  plt.xlabel("Time after scan start (s)", size=15)
  plt.ylabel("Leakage current ({0}A)".format("u"), size=15)
  plt.grid(True)
  #plt.savefig('plot_{}.png'.format(file), dpi=800)
  #plt.savefig('{}.pdf'.format(sys.argv[1][:-4]), dpi=1600)
  plt.show()
  #input()
  
  #os.system("evince --class=test {}.pdf".format(sys.argv[1][:-4]))
  
  
#  plt.close()

else:
  print("Erstes Argument: Pfad zu Textdatei")
  print("Zweites Argument: Anzahl an Scan Channels")
  print("Drittes Argument: Grenze des Leckstroms in uA") 
  #print("Falsche Benutzung!")
