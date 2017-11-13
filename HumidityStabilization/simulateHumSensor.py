#/usr/bin/python3

import random
import time

while True:
  f = open("humidity", 'w')
  a = 100*random.random()
  print(a)
  f.write(str(a))
  f.close()
  time.sleep(2)