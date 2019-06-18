# License: GNU General Public License version 2 (GPLv2)
# (C) 2019 Matthias H. Richter
# - for Alicat mass flow controller and meter
# - set the flow rate and gas type of flow controller and meter for CO2r experiments
# - address of flow meter is fixed
# - accepts three parameters:
# (1) flow controller address
# (2) flow rate
# (3) gas type
# e.g. 'setflow.py B 2.0 CO2'

import sys
import time
import serial
from alicat import FlowController

total = len(sys.argv) 
# get the arguments list 
cmdargs = str(sys.argv)

# parsing args one by one 
address_flowcontroller = str(sys.argv[1])
flowrate = float(sys.argv[2])
gas_type = str(sys.argv[3])

serialport = 'COM3'
resetwait = 10;
flowmeterport = 'C';

# COM port is sometimes busy, why?
# trying to reset serial connection
value = True
while value:
	try:
		ser = serial.Serial(
			port=serialport,
			baudrate=9600,
			timeout=1,
			inter_byte_timeout=1
		)
#		ser.close()
#		ser.open()
		ser.close()
		value = False
	except Exception:
		print('Serial Error1 ...')
		print('Trying again in a few seconds ...')
		time.sleep(resetwait)
		value = True

value = True
while value:
	try:
		flow_controller = FlowController(port=serialport)
		print('Connecting ...')
		flow_controller = FlowController(address=address_flowcontroller)
		flow_meter = FlowController(address=flowmeterport)
		flow_controller.close()
		flow_meter.close()
		flow_controller = FlowController(address=address_flowcontroller)
		flow_meter = FlowController(address=flowmeterport)
		time.sleep(2)
		print('Set flowrate ...')
		flow_controller.set_flow_rate(flowrate)
		time.sleep(2)
		print('Set gas type on flow controller ...')
		flow_controller.set_gas(gas_type)
		time.sleep(2)
		print('\nGet flow controller settings:')
		print(flow_controller.get())
		print('\n')
		if flowrate>0:
			print('Set gas type on flow meter ...')
			flow_meter.set_gas(gas_type)
			print('\nGet flow meter settings:')
			print(flow_meter.get())
			print('\n')
			time.sleep(2)
		flow_controller.close()
		flow_meter.close()
		value = False
	except Exception:
		flow_controller.close()
		flow_meter.close()
		print('Serial Error2 ...')
		print('Trying again in a few seconds ...')
		time.sleep(resetwait)
		value = True

print('Done ...')
time.sleep(5)
