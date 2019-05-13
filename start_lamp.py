# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019 Matthias H. Richter
# remotely starts Oriel Instruments lamp
import serial
import sys
import os
import time

serialport = 'COM1'

if sys.platform == 'win32':
	os.system('cls') # for windows users
else:
	os.system('clear') # for unix users


# configure the serial connections
ser = serial.Serial(
    port=serialport,
    baudrate=9600
)
ser.close()
ser.open()
if not ser.isOpen():
  print('Serial port error')
  sys.exit(1)
  
ser.write(str.encode('START\r\n'))
time.sleep(1)

ser.close()
