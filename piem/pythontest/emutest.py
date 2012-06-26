import emulator
import time

emulator.init()

emulator.digital_write(1, 1)
time.sleep(2)
emulator.digital_write(2, 1)
time.sleep(2)
emulator.digital_write(3, 1)
time.sleep(2)
emulator.digital_write(5, 1)

time.sleep(2)

while True:
	print bin(emulator.read_input())
	time.sleep(2)
