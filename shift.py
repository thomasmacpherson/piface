import pfio
from time import sleep

pfio.init()

TEST_MODE = True

def delay():
	global TEST_MODE
	if TEST_MODE:
		sleep(1)
		
def shift_out(data_pin, latch_pin, clock_pin, edian, data):
""" shift_out takes as arguments:
	the data pin which the bits should be shifted out onto
	the latch pin which connects to the shift register to signify data transfer
	the clock pin for the chip to identify each bit being shifted out
	the edian (most/least significant bit first)
	the data as a byte or series of bytes
"""

	delay()	
	print "clock pin low"
	pfio.digital_write(clock_pin, 0) # set clock low incase it was not already
	delay()
	print "Latch pin low"
	pfio.digital_write(latch_pin,0) # set latch low to notify the chip to receive data

	delay()
	
	data_bits = str(bin(data)[2:].zfill(8))


	if edian:	# if most significant bit first

		for bit in data_bits: 			# loop through the bits of the byte
			bit = int(bit)
			print bit
			pfio.digital_write(data_pin, bit)
			delay()
			pulse_clock(clock_pin)

	else:		# if least significant bit first
	
		for bit in reversed(data_bits):		# loop through the bits of the byte
			bit = int(bit)			# convert to int	
			print bit
			pfio.digital_write(data_pin, bit)	# write bit to pin
			delay()
			pulse_clock(clock_pin)		# pulse the clock high then low for chip to sample the bit

	delay()
	print "latch pin high"
	pfio.digital_write(latch_pin,1)			# set latch high to notify the chip to stop receiving data





def pulse_clock(clock_pin):
""" pulses the clock high then low on the specified clock pin
"""
	print "clock high"
	pfio.digital_write(clock_pin, 1)	# set clock high
	delay()	
	print "clock low"
	pfio.digital_write(clock_pin, 0)	# set clock low
	delay()




# test
data = 101
shift_out(1,2,4,1,data)

print "in reverse"

shift_out(1,2,4,0,data)
