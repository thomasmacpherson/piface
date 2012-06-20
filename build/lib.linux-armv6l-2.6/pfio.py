#!/usr/bin/env python
"""
PFIO.py
Provides I/O methods for interfacing with the RaspberryPi interface (piface)

Notes
20/06/2012 - Thomas Preston (prestotx)
tidied up the code, reordered methods and fixed one or two bugs
now using underscores for function names since this is closer to the PEP-8
(http://www.python.org/dev/peps/pep-0008/#function-names).
Method 'send': We are passing this a list of data and then only handling the
first one. I have changed this to handle every item in the list.
"""
import spi
from time import sleep


VERBOSE_MODE = True # toggle verbosity
PFIO_PRINT_PREFIX = "PFIO: " # prefix for pfio messages

# SPI operations
WRITE_CMD = 0x40
READ_CMD  = 0x41

# Port configuration
IODIRA = 0x00 # I/O direction A
IODIRB = 0x01 # I/O direction B
IOCON  = 0x0A # I/O config
GPIOA  = 0x12 # port A
GPIOB  = 0x13 # port B
GPPUA  = 0x0C # port A pullups
GPPUB  = 0x0D # port B pullups
OUTPUT_PORT = GPIOA
INPUT_PORT  = GPIOB

spi_handler = None

def init():
	"""Initialises the PiFace"""
	if VERBOSE_MODE:
		 #print "PIFO: initialising SPI mode, reading data, reading length . . . \n"
		 pfio_print("initialising SPI")

	global spi_handler
	spi_handler = spi.SPI(0,0) # spi.SPI(X,Y) is /dev/spidevX.Y

	# set up the ports
	write(IOCON,  8)    # enable hardware addressing
	write(IODIRA, 0)    # set port A as outputs
	write(IODIRB, 0xFF) # set port B as inputs
	write(GPIOA,  0xFF) # set port A on
	#write(GPIOB,  0xFF) # set port B on
	write(GPPUB,  0xFF) # set port B pullups on

def deinit():
	"""Deinitialises the PiFace"""
	spi_handler.close()

def pfio_print(text):
	"""Prints a string with the pfio print prefix"""
	print "%s %s" % (PFIO_PRINT_PREFIX, text)

def get_pin_bit_mask(pin_number):
	"""Translates a pin number to pin bit mask. First pin is pin1 (not pin0).
	pin3 = 0b00000100
	pin4 = 0b00001000

	TODO: throw and exception if the pin number is out of range
	"""
	#return 2**(pin-1)
	return 1 << (pin - 1) # shifting makes more sense

def build_hex_string(items):
	"""Builds a hexidecimal string comprised of the given items"""
	hex_string = ""
	for item in items:
		hex_string += "%02x" % item # 10 = 0a
	return hex_string

def digital_write(pin_number, value):
	"""Writes the value given to the pin specified"""
	if VERBOSE_MODE:
		pfio_print("digital write start")

	pin_bit_mask = get_pin_bit_mask(pin_number)

	if VERBOSE_MODE:
		pfio_print("pin bit mask: %s" % bin(pin_bit_mask))

	old_pin_values = read_output()[2]

	if VERBOSE_MODE:
		pfio_print("old pin values: %s" % bin(old_pin_values))

	# generate the 
	if value:
		new_pin_values = old_pin_values | pin_bit_mask
	else:
		new_pin_values = old_pin_values & ~pin_bit_mask

	if VERBOSE_MODE:
		pfio_print("new pin values: %s" % bin(new_pin_values))

	data_as_hex = build_hex_string((WRITE_CMD, OUTPUT_PORT, new_pin_values))

	# send is expecting a list
	data = list()
	data.append(data_as_hex)
	send(data)

	if VERBOSE_MODE:
		pfio_print("digital write end")

def digital_read(pin_number):
	"""Returns the value of the pin specified"""
	current_pin_values = read_input()[2]
	pin_bit_mask = pin_translation(pin_number)

	result = current_pin_values & pin_bit_mask

	# is this correct? -thomas preston
	if result:
		pin = 0
	else:
		pin = 1

	return pin

"""
Some wrapper functions so the user doesn't have to deal with
ugly port variables
"""
def read_output():
	"""Returns the values of the output pins"""
	return read(OUTPUT_PORT)

def read_input():
	"""Returns the values of the input pins"""
	return read(INPUT_PORT)

def write_output(data):
	"""Writed the values of the output pins"""
	return write(OUTPUT_PORT, data)

def write_input(data):
	"""Returns the values of the input pins"""
	return write(INPUT_PORT, data)


def read(port):
	"""Reads from the port specified"""
	# data byte is padded with 1's since it isn't going to be used
	data_as_hex = build_hex_string((READ_CMD, port, "ff"))
	return send([data_as_hex]) # send is expecting a list

def write(port, data):
	"""Writes data to the port specified"""
	data_as_hex = build_hex_string((WRITE_CMD, port, data))
	return send([data_as_hex]) # send is expecting a list


def send(data):
	"""Sends a list of data to the PiFace"""
	# a place to store the returned values for each transfer
	returned_values_list = list() 

	for datum in data:
		# calculates the length, and devides by 2 for two bytes of data sent.
		length_data = len(datum) / 2 # why? -thomas preston

		if VERBOSE_MODE:
		 pfio_print("transfering data: %s" % data)

		# transfer the data string
		returned_values = a.transfer(data[0], length_data)
		returned_values_list.append(returned_values)

		if VERBOSE_MODE:
			pfio_print("SPI module returned:")
			print [hex(value) for value in returned_values]

	return returned_values_list


"""Boiler plate stuff"""
def test_method():
	digital_write(1,1)
	sleep(2)
	digital_write(1,0)

if __name__ == "__main__":
	init()

	#pin1 = digital_read(1)
	#pin2 = digital_read(2)
	#pin3 = digital_read(3)
	#pin4 = digital_read(2)
	#print pin4
	#print "Pin 1= {0}".format(pin1)
	#print "Pin 2= {0}".format(pin2)
	#print "Pin 3= {0}".format(pin3)
	#print "Pin 4= {0}".format(pin4)

	test_method()

	deinit()
