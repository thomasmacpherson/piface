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
from gtk import gdk
from math import pi

status = 0

# pin circle locations
ledsX = [183.0,183.0,222.0,239.0]
ledsY = [135.0,78.0,27.0,27.0]
switchesX = [15.0, 40.0, 65.0, 90.0]
switchesY = [160.0, 160.0, 160.0, 160.0]
relay1PinsX = [285.0,285.0,285.0,]
relay1PinsY = [73.0,86.0,98.0]
relay2PinsX = [285.0,285.0,285.0]
relay2PinsY = [124.0,136.0,148.0]
boardInputPinsX = [6.0,19.0,31.0,44.0,56.0,68.0,80.0,92.0,104]
boardInputPinsY = [186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0]
boardOutputPinsX = [181.0,194.0,206.0,218.0,230.0,242.0,254.0,266.0,278.0]
boardOutputPinsY = [8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0]

RELAY_PIN_PATTERN_ON  = (0, 1, 1)
RELAY_PIN_PATTERN_OFF = (1, 1, 0)

HIGH = 1
LOW = 0
INPUT = 1
OUTPUT = 0
pinModes = 0


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


class Item(object):
	"""A virtual item connected to a pin on the RaspberryPi emulator"""
	def __init__(self, pin_number, is_input=False):
		# an item defaults to an output device
		self.pin_number = pin_number
		self.is_input = is_input
		self.value = 0

	def turn_on(self):
		#print "turning on"
		self.value = 1;
	
	def turn_off(self):
		#print "turning off..."
		self.value = 0;

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
			cr.set_source_rgb(1,1,0)
			cr.arc (self.x, self.y, 5, 0, 2*pi);
			cr.fill()
			cr.restore()

class LED(Item):
	"""A virtual LED on the RaspberryPi emulator"""
	def __init__(self, led_number):
		self.x = ledsX[led_number-1]
		self.y = ledsY[led_number-1]

		if led_number == 1:
			pin_number = PH_PIN_LED_1
		elif led_number == 2:
			pin_number = PH_PIN_LED_2
		elif led_number == 3:
			pin_number = PH_PIN_LED_3
		else:
			pin_number = PH_PIN_LED_4

		Item.__init__(self, pin_number)

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
	def __init__(self, relay_number):
		if relay_number == 1:
			pin_number = PH_PIN_RELAY_1
			self.pins = [Pin(i, False, True, False) for i in range(3)]
		else:
			pin_number = PH_PIN_RELAY_2
			self.pins = [Pin(i, False, False, True) for i in range(3)]

		self._value = 0 # hidden value for property stuff
		self.pins[0].value, \
			self.pins[1].value, \
			self.pins[2].value = RELAY_PIN_PATTERN_OFF

		Item.__init__(self, pin_number)
	
	def _get_value(self):
		return self._value

	def _set_value(self, new_value):
		# set the pins
		if new_value >= 1:
			self.pins[0].value, \
				self.pins[1].value, \
				self.pins[2].value = RELAY_PIN_PATTERN_ON
		else:
			self.pins[0].value, \
				self.pins[1].value, \
				self.pins[2].value = RELAY_PIN_PATTERN_OFF

		self._value = new_value

	def draw(self, cr):
		for pin in self.pins:
			#print "Drawing from relay %d" % self.pin_number
			pin.draw(cr)

class Switch(Item):
	"""A virtual switch on the RaspberryPi emulator"""
	def __init__(self, switch_number):
		self.x = switchesX[switch_number-1]
		self.y = switchesY[switch_number-1]

		if switch_number == 1:
			switch_number = PH_PIN_SWITCH_1
		elif switch_number == 2:
			switch_number = PH_PIN_SWITCH_2
		elif switch_number == 3:
			switch_number = PH_PIN_SWITCH_3
		else:
			switch_number = PH_PIN_SWITCH_4

		Item.__init__(self, switch_number, True)

	def draw_hidden(self, cr):
		cr.arc(self.x, self.y, 5, 0, 2*pi)

	def draw(self, cr):
		if self.value == 1:
			cr.save()
			cr.set_source_rgb(1,1,0)
			cr.arc (self.x, self.y, 5, 0, 2*pi);
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

	## When expose event fires, this is run
	def do_expose_event( self, widget, event ):
		self.cr = self.window.cairo_create( )
		## Call our draw function to do stuff.
		self.draw()

	def _mouseMoved ( self, widget, event ):
		self.x = event.x
		self.y = event.y
		self.queue_draw_area(0, 0, 350, 350)


class EmulatorScreen(Screen):
	"""This class is also a Drawing Area, coming from Screen."""
	def __init__ (self, w, h, speed):
		Screen.__init__(self, w, h, speed)
		self.switches = [Switch(i) for i in range(1,5)] # make four switches
		self.input_pins = [Pin(i, True) for i in range(1,10)] # make nine input Pins
		self.leds = [LED(i) for i in range(1,5)] # make four LED's
		self.relays = [Relay(i) for i in range(1,3)] # make two relays
		self.output_pins = [Pin(i) for i in range(1,10)] # make nine output pins

	def draw(self):
		cr = self.cr # Shabby shortcut.
		#---------TOP LEVEL - THE "PAGE"
		self.cr.identity_matrix  ( ) # VITAL LINE :: I'm not sure what it's doing.
		cr.save ( ) # Start a bubble

		# create the background surface
		self.surface = cairo.ImageSurface.create_from_png("pi.png")
		cr.set_source_surface(self.surface, 0, 0)

		# blank everything
		cr.rectangle( 0, 0, 350, 250 )
		#cr.set_source_rgb( 1,0,0 )
		cr.set_source_surface(self.surface, 0, 0)
		cr.fill()
		cr.new_path() # stops the hit shape from being drawn
		cr.restore()

		# detect clicks on the switches (TODO: this should be roll over)
		for switch in self.switches:
			switch.draw_hidden(cr) 
			if self.mouse_hit(cr):
				if switch.value == 1:
					switch.turn_off()
				else:
					switch.turn_on()

		# detect clicks on the input input_pins
		for pin in self.input_pins:
			pin.draw_hidden(cr) 
			if self.mouse_hit(cr):
				if pin.value == 1:
					pin.turn_off()
				else:
					pin.turn_on()

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

	def mouse_hit(self, cr):
		cr.save ( ) # Start a bubble
		cr.identity_matrix ( ) # Reset the matrix within it.
		hit = cr.in_fill ( self.x, self.y ) # Use Cairo's built-in hit tes
		cr.new_path ( ) # stops the hit shape from being drawn
		cr.restore ( ) # Close the bubble like this never happened.
		return hit

	def _button_press( self, widget, event ):
		self.x = event.x
		self.y = event.y
		self.queue_draw_area(0, 0, 350, 350)

	def _mouseMoved(self, widget, event):
		#self.queue_draw_area(0, 0, 350, 350)
		#print "The mouse is at (%d, %d)" % (event.x, event.y)
		pass

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


def get_pin_bit_mask(pin):
	return 1 << (pin-1)

def digital_read(pin):
	checkPinMode(pin, INPUT)
	global inputPins
	print 'Read of pin {}'.format(pin)
	pin = pinTranslation(pin)
	pin = pin & inputPins
	if pin:
		pin = 1
	print pin
	return pin


def digital_write(pin,status):
	global outputPins
	pin = pinTranslation(pin)
	if status:
		outputPins = outputPins | pin
	else:
		pin = ~pin
		outputPins = outputPins & pin

		print 'Output pins {}'.format(outputPins)

"""
def physically_change_pin(pin):
	global inputPins
	pin +=1
	pin = pinTranslation(pin)

	if status:
		inputPins = inputPins | pin
	else:
		inputPins = intputPins & ~pin

	print "Input pins"
	print inputPins
"""

def run(Widget, w, h, speed):
	window = gtk.Window()
	window.connect("delete-event", gtk.main_quit)
	widget = Widget(w, h, speed)
	widget.show()
	window.add(widget)
	window.present()
	gtk.main()

if __name__ == "__main__":
	run(EmulatorScreen, 292, 193, speed=20)
