##    cairo demos Copyright  (C)  2007 Donn.C.Ingle
##
##    Contact: donn.ingle@gmail.com - I hope this email lasts.
##
##    This program is free software; you can redistribute it and/or modify
##    it under the terms of the GNU General Public License as published by
##    the Free Software Foundation; either version 2 of the License, or
##     ( at your option )  any later version.
##
##    This program is distributed in the hope that it will be useful,
##    but WITHOUT ANY WARRANTY; without even the implied warranty of
##    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##    GNU General Public License for more details.
##
##    You should have received a copy of the GNU General Public License
##    along with this program; if not, write to the Free Software
##    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import pygtk
import gtk, gobject, cairo
import threading
from gtk import gdk
from math import pi
import time
import warnings

import piface.emulator_parts as emulator_parts
from emulator_parts import Item
from emulator_parts import LED
from emulator_parts import Relay
from emulator_parts import Switch


VERBOSE_MODE = False

import pfio
try:
	pfio.init()
	PFIO_CONNECT = True
except pfio.spi.error:
	print "Could not connect to the SPI module (check privileges)."
	PFIO_CONNECT = False

DEFAULT_SPACING = 10

EMU_WIDTH  = 292
EMU_HEIGHT = 193
EMU_SPEED  = 20
emulator_parts.emu_print_PREFIX = "EMU:"


# global variables are bad, AND YOU SHOULD FEEL BAD!
emu_window = None
emu_screen = None


class Emulator(threading.Thread):
	def __init__(self):
		gtk.gdk.threads_init() # init the gdk threads
		threading.Thread.__init__(self)

	def run(self):
		global emu_window
		emu_window = gtk.Window()
		emu_window.connect("delete-event", gtk.main_quit)

		global emu_screen
		if PFIO_CONNECT:
			emu_screen = emulator_parts.EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED, pfio)
		else:
			emu_screen = emulator_parts.EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED)

		emu_screen.finished_setting_up()
		emu_screen.show()

		output_override_section = \
				emulator_parts.OutputOverrideSection(emu_screen.output_pins)
		output_override_section.show()

		container = gtk.HBox(homogeneous=True, spacing=DEFAULT_SPACING)
		container.pack_start(emu_screen)
		container.pack_start(output_override_section)
		container.show()

		emu_window.add(container)
		emu_window.present()
		gtk.main()

"""Input/Output functions mimicing the pfio module"""
def init():
	"""Initialises the RaspberryPi emulator"""
	rpi_emulator = Emulator()
	rpi_emulator.start()
	time.sleep(0.1)

def deinit():
	"""Deinitialises the PiFace"""
	global emu_window
	emu_window.destroy()

	gtk.main_quit()

	global emu_screen
	emu_screen = None

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
		emulator_parts.emu_print("digital write start")

	global emu_screen
	if value >= 1:
		emu_screen.output_pins[pin_number-1].turn_on()
	else:
		emu_screen.output_pins[pin_number-1].turn_off()
	
	#emu_screen.qdraw()

	if VERBOSE_MODE:
		emulator_parts.emu_print("digital write end")

def digital_read(pin_number):
	"""Returns the value of the pin specified"""
	global emu_screen
	return emu_screen.input_pins[pin_number-1].value

"""
Some wrapper functions so the user doesn't have to deal with
ugly port variables
"""
def read_output():
	"""Returns the values of the output pins"""
	global emu_screen
	output_pin_values = [pin.value for pin in emu_screen.output_pins]
	output_binary_string = "".join(map(str, output_pin_values))
	return [None, None, int(output_binary_string, 2), None, None, None]

def read_input():
	"""Returns the values of the input pins"""
	global emu_screen
	input_pin_values = [pin.value for pin in emu_screen.input_pins]
	input_pin_values.reverse() # values are mapped the opposite way
	input_binary_string = "".join(map(str, input_pin_values))
	inverted_input = int(input_binary_string, 2) ^ 0b11111111 # input is active low
	return [None, None, inverted_input, None, None, None]

def write_output(data):
	"""Writes the values of the output pins"""
	output_binary_string = bin(data)[2:].zfill(8) # get an 8 char binary string
	global emu_screen
	for i in range(8):
		if output_binary_string[i] >= 1:
			emu_screen.output_pins[i].turn_on()
		else:
			emu_screen.output_pins[i].turn_off()

	#emu_screen.qdraw()

def write_input(data):
	"""Writes the values of the input pins"""
	input_binary_string = bin(data)[2:].zfill(8) # get an 8 char binary string
	global emu_screen
	for i in range(8):
		if input_binary_string[i] >= 1:
			emu_screen.input_pins[i].turn_on()
		else:
			emu_screen.input_pins[i].turn_off()

	#emu_screen.qdraw()

if __name__ == "__main__":
	init()
