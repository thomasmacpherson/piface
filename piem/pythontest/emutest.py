import emulator
import time

emulator.init()

emulator.digital_write(1, 1)
time.sleep(2)
led1 = emulator.LED(1)
led1.turn_on()
time.sleep(2)
emulator.digital_write(3, 1)
time.sleep(2)
emulator.digital_write(5, 1)

time.sleep(2)

while True:
	print bin(emulator.read_input()[2])
	time.sleep(2)
