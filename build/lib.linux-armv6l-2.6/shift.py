import pfio

pfio.init()


def shift_out(data_pin, latch_pin, clock_pin, edian, data):
	pfio.digital_write(latch_pin,0)
	pfio.digital_write(clock_pin, 0)
	data_bits = str(bin(data)[2:].zfill(8))


	if edian:

		for bit in data_bits:
			bit = int(bit)
			pfio.digital_write(data_pin, bit)
			pulse_clock(clock_pin)

	else:
		for bit in reversed(data_bits):
			bit = int(bit)
			pfio.digital_write(data_pin, bit)
			pulse_clock(clock_pin)

	pfio.digital_write(latch_pin,1)


def pulse_clock(clock_pin):
	pfio.digital_write(clock_pin, 1)
	pfio.digital_write(clock_pin, 0)


data = 234
shift_out(1,2,4,1,data)
