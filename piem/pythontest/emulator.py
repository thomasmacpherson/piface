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


VERBOSE_MODE = False

VIRT_PI_IMAGE = "/home/X09/prestotx/raspberry_pi/piface/piem/pythontest/pi.png"

EMU_WIDTH  = 292
EMU_HEIGHT = 193
EMU_SPEED  = 20
EMU_PRINT_PREFIX = "EMU:"

PIN_COLOUR_R = 0
PIN_COLOUR_G = 1
PIN_COLOUR_B = 1

# pin circle locations
ledsX = [183.0,183.0,222.0,239.0]
ledsY = [135.0,78.0,27.0,27.0]
switchesX = [14.3, 39.3, 64.3, 89.3]
switchesY = [157.5, 157.5, 157.5, 157.5]
relay1PinsX = [285.0,285.0,285.0]
relay1PinsY = [124.0,136.0,148.0]
relay2PinsX = [285.0,285.0,285.0,]
relay2PinsY = [73.0,86.0,98.0]
boardInputPinsX = [6.0,19.0,31.0,44.0,56.0,68.0,80.0,92.0,104]
boardInputPinsY = [186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0]
boardOutputPinsX = [181.0,194.0,206.0,218.0,230.0,242.0,254.0,266.0,278.0]
boardOutputPinsY = [8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0]

RELAY_PIN_PATTERN_ON  = (0, 1, 1)
RELAY_PIN_PATTERN_OFF = (1, 1, 0)

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

emu_window = None
emu_screen = None


class Item(object):
	"""A virtual item connected to a pin on the RaspberryPi emulator"""
	def __init__(self, pin_number, is_input=False):
		# an item defaults to an output device
		self.pin_number = pin_number
		self.is_input = is_input

		self._value = 0 # hidden value for property stuff
		self._hold  = False # this value cannot be changed unless forced
		self._force = False # when true, held values can be changed
	
	def _get_value(self):
		return self._value

	def _set_value(self, new_value):
		if not self._hold or (self._hold and self._force):
			self._value = new_value
			self._hold  = False
			self._force = False

			global emu_screen
			if emu_screen:
				emu_screen.qdraw()

	value = property(_get_value, _set_value)

	def turn_on(self, hold=False):
		#print "turning on"
		self.value = 1;
		self._hold = hold

	def turn_off(self, force=False):
		#print "turning off..."
		self._force = force
		self.value = 0;
	
	def attach_pin(self, pin, pin_number=1, is_input=False):
		if pin:
			self.attached_pin = pin
		elif emu_screen:
			if is_input:
				self.attached_pin = emu_screen.input_pins[pin_number-1]
			else:
				self.attached_pin = emu_screen.output_pins[pin_number-1]
		else: # guess
			if is_input:
				self.attached_pin = Pin(pin_number)
			else:
				self.attached_pin = Pin(pin_number)

class Pin(Item):
	def __init__(self, pin_number, is_input=False,
			is_relay1_pin=False, is_relay2_pin=False):
		if is_relay1_pin:
			self.x = relay1PinsX[pin_number]
			self.y = relay1PinsY[pin_number]
		elif is_relay2_pin:
			self.x = relay2PinsX[pin_number]
			self.y = relay2PinsY[pin_number]
		elif is_input:
			self.x = boardInputPinsX[pin_number-1]
			self.y = boardInputPinsY[pin_number-1]
		else:
			self.x = boardOutputPinsX[pin_number-1]
			self.y = boardOutputPinsY[pin_number-1]

		Item.__init__(self, pin_number, is_input)

	def draw_hidden(self, cr):
		cr.arc(self.x, self.y, 5, 0, 2*pi)

	def draw(self, cr):
		if self.value == 1:
			#print "drawing pin at %d, %d" % (self.x, self.y)
			cr.save()
			cr.set_source_rgb(PIN_COLOUR_R,PIN_COLOUR_G,PIN_COLOUR_B)
			cr.arc (self.x, self.y, 5, 0, 2*pi);
			cr.fill()
			cr.restore()

class LED(Item):
	"""A virtual LED on the RaspberryPi emulator"""
	def __init__(self, led_number, attached_pin=None):
		self.attach_pin(attached_pin, led_number)

		self.x = ledsX[led_number-1]
		self.y = ledsY[led_number-1]

		Item.__init__(self, led_number)

	def _get_value(self):
		return self.attached_pin.value

	def _set_value(self, new_value):
		self.attached_pin.value = new_value
	
	value = property(_get_value, _set_value)

	def turn_on(self):
		#print "turning on LED"
		self.value = 1;
	
	def turn_off(self):
		#print "turning off..."
		self.value = 0;

	def draw(self, cr):
		"""
		Draw method requires cr drawing thingy (technical term)
		to be passed in
		"""
		if self.value == 1:
			# draw the yellow circle (r=8)
			cr.save()
			cr.set_source_rgb(1,1,0)
			cr.arc (self.x, self.y, 8, 0, 2*pi);
			cr.fill()
			cr.restore()

			# draw the red circle (r=6)
			cr.save()
			cr.set_source_rgb(1,0,0)
			cr.arc (self.x, self.y, 6, 0, 2*pi);
			cr.fill()
			cr.restore()

class Relay(Item):
	"""A relay on the RaspberryPi"""
	def __init__(self, relay_number, attached_pin=None):
		self.attach_pin(attached_pin, relay_number)

		if relay_number == 1:
			self.pins = [Pin(i, False, True, False) for i in range(3)]
		else:
			self.pins = [Pin(i, False, False, True) for i in range(3)]

		Item.__init__(self, relay_number)

		self.value = self.attached_pin.value

	def _get_value(self):
		return self.attached_pin.value

	def _set_value(self, new_value):
		self.attached_pin.value = new_value
		self.set_pins()

	value = property(_get_value, _set_value)

	def set_pins(self):
		if self.value >= 1:
			self.pins[0].value, \
				self.pins[1].value, \
				self.pins[2].value = RELAY_PIN_PATTERN_ON
		else:
			self.pins[0].value, \
				self.pins[1].value, \
				self.pins[2].value = RELAY_PIN_PATTERN_OFF

	def turn_on(self):
		self.value = 1;
	
	def turn_off(self):
		self.value = 0;

	def draw(self, cr):
		self.set_pins()
		for pin in self.pins:
			#print "Drawing from relay %d" % self.pin_number
			pin.draw(cr)

class Switch(Item):
	"""A virtual switch on the RaspberryPi emulator"""
	def __init__(self, switch_number, attached_pin=None):
		self.attach_pin(attached_pin, switch_number, True)

		self.x = switchesX[switch_number-1]
		self.y = switchesY[switch_number-1]
		Item.__init__(self, switch_number, True)

	def _get_value(self):
		return self.attached_pin.value

	def _set_value(self, new_value):
		self.attached_pin.value = new_value
	
	value = property(_get_value, _set_value)

	def turn_on(self):
		#print "turning on"
		self.value = 1;
	
	def turn_off(self):
		#print "turning off..."
		self.value = 0;

	def draw_hidden(self, cr):
		cr.arc(self.x, self.y, 5, 0, 2*pi)

	def draw(self, cr):
		if self.value == 1:
			cr.save()
			cr.set_source_rgb(1,1,0)
			cr.arc (self.x, self.y, 4.5, 0, 2*pi);
			cr.fill()
			cr.restore()


class Screen(gtk.DrawingArea):
	""" This class is a Drawing Area"""
	def __init__(self, w, h, speed ):
		super(Screen, self).__init__()

		## Old fashioned way to connect expose. I don't savvy the gobject stuff.
		self.connect("expose_event", self.do_expose_event)

		## We want to know where the mouse is:
		self.connect("motion_notify_event", self._mouseMoved)
		self.connect("button_press_event", self._button_press)

		## More GTK voodoo : unmask events
		self.add_events(gdk.BUTTON_PRESS_MASK | gdk.BUTTON_RELEASE_MASK | gdk.POINTER_MOTION_MASK)
		self.width, self.height = w, h
		self.set_size_request(w, h)
		self.x, self.y = 11110,11111110 # unlikely first coord to prevent false hits.

		self.button_pressed = False # check if it was a mouse move or button

	## When expose event fires, this is run
	def do_expose_event(self, widget, event):
		self.cr = self.window.cairo_create( )
		## Call our draw function to do stuff.
		self.draw()

	def _mouseMoved(self, widget, event):
		self.x = event.x
		self.y = event.y
		self.button_pressed = False
		self.queue_draw_area(0, 0, 350, 350)

	def _button_press(self, widget, event):
		self.x = event.x
		self.y = event.y
		self.button_pressed = True
		self.queue_draw_area(0, 0, 350, 350)
	
	def qdraw(self):
		"""Register a draw to be made"""
		self.queue_draw_area(0, 0, 350, 350)

class EmulatorScreen(Screen):
	"""This class is also a Drawing Area, coming from Screen."""
	def __init__ (self, w, h, speed):
		Screen.__init__(self, w, h, speed)
		self.input_pins = [Pin(i, True) for i in range(1,9)]
		self.switches = [Switch(i+1, self.input_pins[i]) for i in range(4)]

		self.output_pins = [Pin(i) for i in range(1,10)]
		self.relays = [Relay(i+1, self.output_pins[i]) for i in range(2)]
		self.leds = [LED(i+1, self.output_pins[i]) for i in range(4)]

	def draw(self):
		cr = self.cr # Shabby shortcut.
		#---------TOP LEVEL - THE "PAGE"
		self.cr.identity_matrix  ( ) # VITAL LINE :: I'm not sure what it's doing.
		cr.save ( ) # Start a bubble

		# create the background surface
		self.surface = cairo.ImageSurface.create_from_png(VIRT_PI_IMAGE)
		cr.set_source_surface(self.surface, 0, 0)

		# blank everything
		cr.rectangle( 0, 0, 350, 250 )
		#cr.set_source_rgb( 1,0,0 )
		cr.set_source_surface(self.surface, 0, 0)
		cr.fill()
		cr.new_path() # stops the hit shape from being drawn
		cr.restore()

		if self.button_pressed:
			self.input_pin_detect(cr)
			self.button_pressed = False # stop registering the press
		else:
			self.switch_detect(cr)

		# draw all the switches
		for switch in self.switches:
			switch.draw(cr)

		# draw all the input_pins
		for pin in self.input_pins:
			pin.draw(cr)

		# draw all leds
		for led in self.leds:
			led.draw(cr)

		# draw all the relay pins
		for relay in self.relays:
			relay.draw(cr)

		# draw all output pins
		for pin in self.output_pins:
			pin.draw(cr)

	def switch_detect(self, cr):
		# detect rollover on the switches
		for switch in self.switches:
			switch.draw_hidden(cr) 
			if self.mouse_hit(cr):
				switch.turn_on()
			else:
				switch.turn_off()

	def input_pin_detect(self, cr):
		# detect clicks on the input input_pins
		for pin in self.input_pins:
			pin.draw_hidden(cr) 
			if self.mouse_hit(cr):
				if pin.value == 1:
					pin.turn_off(True) # force/hold
				else:
					pin.turn_on(True) # force/hold

	def mouse_hit(self, cr):
		cr.save ( ) # Start a bubble
		cr.identity_matrix ( ) # Reset the matrix within it.
		hit = cr.in_fill ( self.x, self.y ) # Use Cairo's built-in hit tes
		cr.new_path ( ) # stops the hit shape from being drawn
		cr.restore ( ) # Close the bubble like this never happened.
		return hit

"""
## Print to the console -- low-tech special effects :)
#        if hit: 
#       	print "HIT!", self.x, self.y

	def drawCairoStuff ( self, bos, col= ( 1,0,0 ) ):
		""This draws the squares we see. Pass it a BagOfStuff (bos) and a colour.""
		cr = self.cr
		## Thrillingly, we draw a rectangle.
		## It's drawn such that 0,0 is in it's center.
		cr.rectangle( -25, -25, 50, 50 )
		cr.set_source_rgb( col[0],col[1],col[2] )
		cr.fill( )
		## Now draw an axis
		#self.guageScale ( )
		## Now a visual indicator of the point of rotation
		cr.set_source_rgb( 1,1,1 )
		cr.rectangle ( bos.rx - 2, bos.ry - 2, 4, 4 )
		cr.fill ( )

	## Same as the rectangle we see. No fill.
	def drawHitShape ( self ):
		""Draws a shape that we'll use to test hits.""
		#self.cr.rectangle( 0, 0, 350, 250 ) # Same as the shape of the squares
		self.cr.arc (15.0, 160.0, 6, 0, 2*pi)
		self.cr.arc (40.0, 160.0, 6, 0, 2*pi)
		self.cr.arc (65.0, 160.0, 6, 0, 2*pi)
		self.cr.arc (90.0, 160.0, 6, 0, 2*pi)
	
	def drawOne(self, index):
		self.cr.arc(boardButtonsX[index],boardButtonsY[index],6,0, 2*pi)
"""

#emu_screen = None
class Emulator(threading.Thread):
	def __init__(self):
		gtk.gdk.threads_init() # init the gdk threads
		threading.Thread.__init__(self)

	def run(self):
		global emu_window
		emu_window = gtk.Window()
		emu_window.connect("delete-event", gtk.main_quit)

		global emu_screen
		emu_screen = EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED)
		emu_screen.show()

		emu_window.add(emu_screen) # add the screen to the window
		emu_window.present()
		gtk.main()

def init():
	"""Initialises the RaspberryPi emulator"""
	rpi_emulator = Emulator()
	rpi_emulator.start()
	time.sleep(0.5)
	
	"""
	EXAMPLE
	global emu_screen
	emu_screen.output_pins[2].turn_on()
	emu_screen.qdraw()

	time.sleep(3)
	emu_screen.output_pins[5].turn_on()
	emu_screen.qdraw()
	"""

def deinit():
	"""Deinitialises the PiFace"""
	global emu_window
	emu_window.destroy()

	gtk.main_quit()

	global emu_screen
	emu_screen = None

def emu_print(text):
	"""Prints a string with the pfio print prefix"""
	print "%s %s" % (EMU_PRINT_PREFIX, text)

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
		emu_print("digital write start")

	global emu_screen
	if value >= 1:
		emu_screen.output_pins[pin_number-1].turn_on()
	else:
		emu_screen.output_pins[pin_number-1].turn_off()
	
	#emu_screen.qdraw()

	if VERBOSE_MODE:
		emu_print("digital write end")

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
