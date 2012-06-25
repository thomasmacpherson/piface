#!/usr/bin/env python
"""
pfio.py
Provides I/O methods for interfacing with the RaspberryPi interface (piface)

piface has two ports (input/output) each with eight pins with several
peripherals connected for interacting with the raspberry pi

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


VERBOSE_MODE = False # toggle verbosity
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

# piface peripheral pin numbers
# each peripheral is connected to an I/O pin
# some pins are connected to many peripherals
# outputs
PH_PIN_LED_1 = 1
PH_PIN_LED_2 = 2
PH_PIN_LED_3 = 3
PH_PIN_LED_4 = 4
PH_PIN_RELAY_1 = 1
PH_PIN_RELAY_2 = 2
# inputs
PH_PIN_SWITCH_1 = 1
PH_PIN_SWITCH_2 = 2
PH_PIN_SWITCH_3 = 3
PH_PIN_SWITCH_4 = 4


spi_handler = None


# custom exceptions
class InitialisationError(Exception):
	pass

class InputDeviceError(Exception):
	pass


# classes
class Item(object):
	"""An item connected to a pin on the RaspberryPi"""
	def __init__(self, pin_number, is_input=False):
		# an item defaults to an output device
		self.pin_number = pin_number
		self.is_input = is_input

	def _get_value(self):
		if not self.is_input:
			raise InputDeviceError("You cannot get the value of an output!")
		else:
			return digital_read(self.pin_number)

	def _set_value(self, data):
		if self.is_input:
			raise InputDeviceError("You cannot set an input's values!")
		else:
			return digital_write(self.pin_number, data)

	value = property(_get_value, _set_value)

	def turn_on(self):
		self.value = 1;
	
	def turn_off(self):
		self.value = 0;

class LED(Item):
	"""An LED on the RaspberryPi"""
	def __init__(self, led_number):
		if led_number == 1:
			pin_number = PH_PIN_LED_1
		elif led_number == 2:
			pin_number = PH_PIN_LED_2
		elif led_number == 3:
			pin_number = PH_PIN_LED_3
		else:
			pin_number = PH_PIN_LED_4

		Item.__init__(self, pin_number)

class Relay(Item):
	"""A relay on the RaspberryPi"""
	def __init__(self, relay_number):
		if relay_number == 1:
			pin_number = PH_PIN_RELAY_1
		else:
			pin_number = PH_PIN_RELAY_2

		Item.__init__(self, pin_number)

class Switch(Item):
	"""A switch on the RaspberryPi"""
	def __init__(self, switch_number):
		if switch_number == 1:
			switch_number = PH_PIN_SWITCH_1
		elif swtich_number == 2:
			switch_number = PH_PIN_SWITCH_2
		elif switch_number == 3:
			switch_number = PH_PIN_SWITCH_3
		else:
			switch_number = PH_PIN_SWITCH_4

		Item.__init__(self, switch_number, True)


# functions/methods/whatever you want to call them
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

	# initialise all outputs to 0
	for pin in range(1, 9):
		digital_write(pin, 0)

def deinit():
	"""Deinitialises the PiFace"""
	spi_handler.close()
	spi_handler = None

def pfio_print(text):
	"""Prints a string with the pfio print prefix"""
	print "%s %s" % (PFIO_PRINT_PREFIX, text)

def get_pin_bit_mask(pin_number):
	"""Translates a pin number to pin bit mask. First pin is pin1 (not pin0).
	pin3 = 0b00000100
	pin4 = 0b00001000

	TODO: throw and exception if the pin number is out of range
	"""
	#return 2**(pin_number-1)
	return 1 << (pin_number - 1) # shifting makes more sense

def get_pin_number(bit_pattern):
	"""Returns the lowest pin number from a given bit pattern"""
	pin_number = 1 # assume pin 1
	while (bit_pattern & 1) == 0:
		bit_pattern = bit_pattern >> 1
		pin_number += 1
		if pin_number > 8:
			pin_number = 0
			break
	
	return pin_number

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
	pin_bit_mask = get_pin_bit_mask(pin_number)

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
	data_as_hex = build_hex_string((READ_CMD, port, 0xff))
	return send([data_as_hex])[0] # send is expecting and returns a list

def write(port, data):
	"""Writes data to the port specified"""
	data_as_hex = build_hex_string((WRITE_CMD, port, data))
	return send([data_as_hex])[0] # send is expecting and returns a list


def send(data):
	"""Sends a list of data to the PiFace"""
	if spi_handler == None:
		raise InitialisationError("The pfio module has not yet been initialised. Before send(), call init().")
	# a place to store the returned values for each transfer
	returned_values_list = list() 

	for datum in data:
		# calculates the length, and devides by 2 for two bytes of data sent.
		length_data = len(datum) / 2 # why? -thomas preston

		if VERBOSE_MODE:
		 pfio_print("transfering data: %s" % data)

		# transfer the data string
		returned_values = spi_handler.transfer(data[0], length_data)
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
