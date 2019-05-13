# Licence: GNU General Public License version 2 (GPLv2)
# (C) 2019 Matthias H. Richter
# connect to Keithley 2182A Nanovoltmeter in dual channel mode
# through serial port and save readings to file
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

strusage = 'Usage:\r\n	-p	Serial port, e.g. COM12\r\n	-f	Filename for saving data.\r\n	-s	Sensing, e.g. VOLT, TEMP'

try:
  opts, args = getopt.getopt(sys.argv[1:], 'f:p:s:',['file=', 'port=', 'sense='])
except getopt.GetoptError as err:
  print('error')
  print(strusage)
  sys.exit(2)

serialport = 'COM12'
savefile = 'KI2182dualdefault.csv'
sensesett = "VOLT" # 'VOLT' or 'TEMP'
#ACDC = "DC"
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
elif sensesett == "TEMP":
  senseunit = '°C'
	

if sys.platform == 'win32':
	os.system('cls') # for windows users
else:
	os.system('clear') # for unix users

print('Reading dual channel data from \x1b[1;31;40mKeithley 2182A Nanovoltmeter\x1b[0m at',serialport)
print('Saving data to:\x1b[1;32;40m',os.getcwd(),'\\',savefile,'\x1b[0m')
print('Exit with Ctrl+C!\r\n')

# configure the serial connections
ser = serial.Serial(
    port=serialport,
    baudrate=9600,
	timeout=1,
	inter_byte_timeout=1
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
idn = 'KEITHLEY INSTRUMENTS INC.,MODEL 2182A'
if not (out[:len(idn)] == idn):
  print('Error. Got IDN:',out,', expected: ',idn)
  sys.exit(1)

# reset Keithley and change settings
ser.write(str.encode('*RST\r\n'))
ser.write(str.encode('*CLS\r\n'))

ser.write(str.encode(':INITiate\r\n'))
ser.write(str.encode(':INITiate:CONTinuous ON\r\n'))

ser.write(str.encode(":SENS:CHAN 2\r\n"))
ser.write(str.encode(":SENS:FUNC '"+sensesett+":DC'\r\n"))

ser.write(str.encode(":SENS:CHAN 1\r\n"))
ser.write(str.encode(":SENS:FUNC '"+sensesett+":DC'\r\n"))

ser.write(str.encode(":SENS:VOLT:CHAN1:RANG:AUTO ON\r\n"))
ser.write(str.encode(":SENS:VOLT:CHAN2:RANG:AUTO ON\r\n"))
ser.write(str.encode(":TRACE:CLEAR\r\n"))

#ser.write(str.encode(":SENS:CHAN 1\r\n"))
#ser.write(str.encode(':sens:data:fres?\r\n'))
#ser.write(str.encode(':FETCh?\r\n'))
#wait before reading output. 
#time.sleep(1)
#outch1=''
#outch1 = ser.read(ser.in_waiting)

time.sleep(5) # give it enough time to change settings

starttime = time.time()
while True :
  #ser.write(str.encode(':FETCh?\r\n'))
  # select channel 1 and get fresh reading
  ser.write(str.encode(":SENS:CHAN 1\r\n"))
  #ser.write(str.encode(':sens:data:fres?\r\n'))
  ser.write(str.encode(':FETCh?\r\n'))
  #wait before reading output. 
  #time.sleep(1)
  outch1=''
  outch1 = ser.read(80)
  #outch1 = ser.read(ser.in_waiting)
  outch1=outch1.decode('ASCII')
  outch1=outch1.rstrip()
  outch1=outch1.replace('\r', '')
  outch1=outch1.replace('\n', '')
  
  # select channel 2 and get fresh reading
  ser.write(str.encode(":SENS:CHAN 2\r\n"))
  #ser.write(str.encode(':sens:data:fres?\r\n'))
  ser.write(str.encode(':FETCh?\r\n'))
  #wait before reading output. 
  #time.sleep(1)
  outch2=''
  outch2 = ser.read(80)
  #outch2 = ser.read(ser.in_waiting)
  outch2=outch2.decode('ASCII')
  outch2=outch2.rstrip()
  outch2=outch2.replace('\r', '')
  outch2=outch2.replace('\n', '')

  if outch1 != '':
      #out=out.rstrip()
      tmptime = time.time()
      m, s = divmod(tmptime-starttime, 60)
      h, m = divmod(m, 60)
      buf = "time: \x1b[1;36;40m%d:%02d:%02d\x1b[0m ; \x1b[1;36;40m%s %s ; %s %s  \x1b[0m     " % (h, m, s,outch1,senseunit,outch2,senseunit)
      print(buf,end="\r", flush=True)
      with open(savefile,"a") as file_a:
        file_a.write(str(tmptime)+','+str(outch1)+','+str(outch2)+'\n')
      file_a.close

ser.close()
