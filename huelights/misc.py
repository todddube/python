import time
from time import sleep

for i in range(101):
    print ('\r'+str(i)+'% completed', time.sleep(0.1))