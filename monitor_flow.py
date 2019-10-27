# License: GNU General Public License version 2 (GPLv2)
# (C) 2019 Matthias H. Richter
# - for Alicat mass flow controller and meter
# - monitor and record data from cotroller/meter
import sys
import time
import serial
import signal
import os
import getopt

def signal_handler(sig, frame):
        print('\r\nYou pressed Ctrl+C!\r\n')
        ser.close()
        sys.exit(0)
        
def save_results(buf, file):
      with open(file,"a") as file_a:
        file_a.write(buf+'\n')
      file_a.close
        
signal.signal(signal.SIGINT, signal_handler)
strusage = 'Usage:\r\n	-p	Serial port, e.g. COM4\r\n	-f	Filename for saving data.\r\n	-c	controller number, e.g. A, B, E'

try:
  opts, args = getopt.getopt(sys.argv[1:], 'f:p:c:',['file=', 'port=', 'controller='])
  if not opts:
    print('error')
    print(strusage)
    sys.exit(2)
except getopt.GetoptError as err:
  print('error')
  print(strusage)
  sys.exit(2)

serialport = 'COM4'
savefile = 'flowdefault.csv'
devicenum = "A"
resetwait = 10;

for o, a in opts:
  if o in ("-f", "--file"):
    savefile = a
  elif o in ("-p", "--port"):
    serialport = a
  elif o in ("-c", "--controller"):
    devicenum = a
  else:
    print('error')
    print(strusage)
    sys.exit(2)

value = True
while value:
	try:
		ser = serial.Serial(
			port=serialport,
			baudrate=9600,
			timeout=1,
			inter_byte_timeout=1
		)
		value = False
	except Exception:
		print('Serial Error1 ...')
		print('Trying again in a few seconds ...')
		time.sleep(resetwait)
		value = True

if sys.platform == 'win32':
	os.system('cls') # for windows users
else:
	os.system('clear') # for unix users

starttime = time.time()
while True:
  time.sleep(1)
  ser.write(str.encode(devicenum+"\r"))
  out=''
  out = ser.read(ser.in_waiting)
  if out != '':
      out=out.rstrip()
      tmptime = time.time()
      m, s = divmod(tmptime-starttime, 60)
      h, m = divmod(m, 60)
      tmp = out.decode('ASCII')
      tmp = tmp.split()
      if (len(tmp)==7):
        #print(len(tmp))
        #print(tmp)
        # 0: controller
        # 1: pressure
        # 2: temperature
        # 3: CCM
        # 4: SCCM
        # 5: setpoint
        # 6: gas
        buf = "time: %d:%02d:%02d ; P: %s; T: %s; CCM: %s; SCCM: %s; gas: %s" % (h, m, s, tmp[1], tmp[2], tmp[3], tmp[4], tmp[6])
        print(buf,end="\r", flush=True)

      if (len(tmp)==6):
        #print(len(tmp))
        #print(tmp)
        # 0: controller
        # 1: pressure
        # 2: temperature
        # 3: CCM
        # 4: SCCM
        # 5: gas
        buf = "time: %d:%02d:%02d ; P: %s; T: %s; CCM: %s; SCCM: %s; gas: %s" % (h, m, s, tmp[1], tmp[2], tmp[3], tmp[4], tmp[5])
        print(buf,end="\r", flush=True)
        save_results(buf, savefile)

ser.close()
