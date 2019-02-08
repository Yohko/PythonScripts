# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019 Matthias H. Richter
# connect to Keithley 2000 Multimeter through serial port and save readings to file
import time
import serial
import sys
import os
import getopt
import signal

def signal_handler(sig, frame):
        print('\r\nYou pressed Ctrl+C!\r\n')
        ser.close()
        sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

strusage = 'Usage:\r\n	-p	Serial port, e.g. COM11\r\n	-f	Filename for saving data.\r\n	-s	Sensing, e.g. VOLT, CURR'

try:
  opts, args = getopt.getopt(sys.argv[1:], 'f:p:s:',['file=', 'port=', 'sense='])
  if not opts:
    print('error')
    print(strusage)
    sys.exit(2)
except getopt.GetoptError as err:
  print('error')
  print(strusage)
  sys.exit(2)

serialport = 'COM11'
savefile = 'KI2000default.csv'
#VOLT:AC, VOLT:DC, RES, CURR:AC, CURR:DC, FREQ, TEMP, PER, DIOD, CONT
sensesett = "VOLT"
ACDC = "DC"
senseunit = "V"

for o, a in opts:
  if o in ("-f", "--file"):
    savefile = a
  elif o in ("-p", "--port"):
    serialport = a
  elif o in ("-s", "--sense"):
    sensesett = a    
  else:
    print('error')
    print(strusage)
    sys.exit(2)

if sensesett == "VOLT":
  senseunit = 'V'
elif sensesett == "CURR":
  senseunit = 'A'
	

if sys.platform == 'win32':
	os.system('cls') # for windows users
else:
	os.system('clear') # for unix users

print('Reading data from \x1b[1;31;40mKeithley 2000 Multimeter\x1b[0m at',serialport)
print('Saving data to:\x1b[1;32;40m',os.getcwd()+savefile,'\x1b[0m')
print('Exit with Ctrl+C!\r\n')

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
  
ser.write(str.encode('*IDN?\r\n'))
time.sleep(1)
out = ser.read(ser.in_waiting)
out = out.rstrip()
out = out.decode('ASCII')
idn = 'KEITHLEY INSTRUMENTS INC.,MODEL 2000'
if not (out[:len(idn)] == idn):
  print('Error. Got IDN:',out,', expected: ',idn)
  sys.exit(1)

# reset Keithley and change settings
ser.write(str.encode('*RST\r\n'))
ser.write(str.encode(':INITiate\r\n'))
ser.write(str.encode(':INITiate:CONTinuous ON\r\n'))
time.sleep(1)
ser.write(str.encode("SENS:FUNC '"+sensesett+":"+ACDC+"'\r\n"))
ser.write(str.encode(":SENS:"+sensesett+":"+ACDC+":RANG:AUTO ON\r\n"))
ser.write(str.encode(":SENS:"+sensesett+":"+ACDC+":AVER:STAT ON\r\n"))
# only DC
#ser.write(str.encode(":SENS:"+sensesett+":"+ACDC+":NPLC 1\r\n")) # 0.01..10 power cycles per integration
ser.write(str.encode(':FORM:ELEM READ\r\n'))
time.sleep(5) # give it enough time to change settings

starttime = time.time()
while True :
  ser.write(str.encode(':FETCh?\r\n'))
  # wait one second before reading output. 
  time.sleep(1)
  out=''
  out = ser.read(ser.in_waiting)
  if out != '':
      out=out.rstrip()
      tmptime = time.time()
      m, s = divmod(tmptime-starttime, 60)
      h, m = divmod(m, 60)
      buf = "time: \x1b[1;36;40m%d:%02d:%02d\x1b[0m ; \x1b[1;36;40m%s %s\x1b[0m   " % (h, m, s,out.decode('ASCII'),senseunit)
      print(buf,end="\r", flush=True)
      with open(savefile,"a") as file_a:
        file_a.write(str(tmptime)+','+str(out.decode('ASCII'))+'\n')
      file_a.close
        
ser.close()
