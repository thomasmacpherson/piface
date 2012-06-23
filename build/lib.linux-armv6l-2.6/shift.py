import pfio
from time import sleep

pfio.init()

TEST_MODE = True

def delay():
	global TEST_MODE
	if TEST_MODE:
		sleep(1)
		
def shift_out(data_pin, latch_pin, clock_pin, edian, data):
	delay()
	print "Latch pin low"
	pfio.digital_write(latch_pin,0)
	delay()	
	print "clock pin low"
	pfio.digital_write(clock_pin, 0)
	delay()
	
	data_bits = str(bin(data)[2:].zfill(8))


	if edian:

		for bit in data_bits:
			bit = int(bit)
			print bit
			pfio.digital_write(data_pin, bit)
			delay()
			pulse_clock(clock_pin)

	else:
		for bit in reversed(data_bits):
			bit = int(bit)
			print bit
			pfio.digital_write(data_pin, bit)
			delay()
			pulse_clock(clock_pin)

	delay()
	print "latch pin high"
	pfio.digital_write(latch_pin,1)



def pulse_clock(clock_pin):
	print "clock high"
	pfio.digital_write(clock_pin, 1)
	delay()	
	print "clock low"
	pfio.digital_write(clock_pin, 0)
	delay()





data = 101
shift_out(1,2,4,1,data)

print "in reverse"

shift_out(1,2,4,0,data)
