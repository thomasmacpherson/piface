import pygtk
pygtk.require("2.0")
import gtk, gobject, cairo
from math import pi


VIRT_PI_IMAGE = "pi.png"
VIRT_LED_ON_IMAGE = "led_on.png"

EMU_PRINT_PREFIX = "EMU:"

PIN_COLOUR_R = 0
PIN_COLOUR_G = 1
PIN_COLOUR_B = 1

# pin circle locations
ledsX = [183.0,183.0,239.0,222.0]
ledsY = [135.0,78.0,27.0,27.0]
switchesX = [14.3, 39.3, 64.3, 89.3]
switchesY = [157.5, 157.5, 157.5, 157.5]
relay1PinsX = [285.0,285.0,285.0]
relay1PinsY = [124.0,136.0,148.0]
relay2PinsX = [285.0,285.0,285.0,]
relay2PinsY = [73.0,86.0,98.0]
boardInputPinsX = [6.0,19.0,31.0,44.0,56.0,68.0,80.0,92.0,104]
boardInputPinsY = [186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0]
"""
# 1 -> 9
boardOutputPinsX = [181.0,194.0,206.0,218.0,230.0,242.0,254.0,266.0,278.0]
boardOutputPinsY = [8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0]
"""
# 8 <- 1
boardOutputPinsX = [266.0, 254.0, 242.0, 230.0, 218.0, 206.0, 194.0, 181.0]
boardOutputPinsY = [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0]

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

emu_screen = None
have_led_image = False

pfio = None # the pfio module that has been passed in


class Item(object):
	"""A virtual item connected to a pin on the RaspberryPi emulator"""
	def __init__(self, pin_number, is_input=False, is_relay_ext_pin=False):
		# an item defaults to an output device
		self.pin_number = pin_number
		self.is_input = is_input
		self.is_relay_ext_pin = is_relay_ext_pin

		self._value = 0 # hidden value for property stuff
		self._hold  = False # this value cannot be changed unless forced
		self._force = False # when true, held values can be changed
	
	def _get_value(self):
		# if the pfio is here then cross reference the virtual input
		# with the physical input
		global pfio
		if pfio and self.is_input:
			self._value = self._value | pfio.digital_read(self.pin_number)

		return self._value

	def _set_value(self, new_value):
		if not self._hold or (self._hold and self._force):
			self._value = new_value
			self._hold  = False
			self._force = False

			global emu_screen
			if emu_screen:
				emu_screen.qdraw()

			global pfio
			if pfio and not self.is_input and not self.is_relay_ext_pin:
				# update the state of the actual output devices
				pfio.digital_write(self.pin_number, new_value)
				#print "Setting pin %d to %d" % (self.pin_number, new_value)

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
			is_relay1_pin=False, is_relay2_pin=False,
			is_relay_ext_pin=False):
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

		Item.__init__(self, pin_number, is_input, is_relay_ext_pin)

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
			global have_led_image
			if have_led_image:
				# draw the illuminated LED
				cr.save()
				led_surface = cairo.ImageSurface.create_from_png(VIRT_LED_ON_IMAGE)
				cr.set_source_surface(led_surface, self.x-6, self.y-8)
				cr.paint()
				cr.restore()
			else:
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
			self.pins = [Pin(i, False, True, False, True) for i in range(3)]
		else:
			self.pins = [Pin(i, False, False, True, True) for i in range(3)]

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
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.BUTTON_RELEASE_MASK | gtk.gdk.POINTER_MOTION_MASK)
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
	def __init__ (self, w, h, speed, pfio_module=None):
		Screen.__init__(self, w, h, speed)

		global have_led_image
		try:
			f = open(VIRT_LED_ON_IMAGE)
			f.close()
			have_led_image = True
		except:
			emu_print("could not find the virtual led image: %s" % VIRT_LED_ON_IMAGE)
			have_led_image = False

		global pfio
		pfio = pfio_module

		self.input_pins = [Pin(i, True) for i in range(1,9)]
		self.switches = [Switch(i+1, self.input_pins[i]) for i in range(4)]

		self.output_pins = [Pin(i) for i in range(1,9)]
		self.relays = [Relay(i+1, self.output_pins[i]) for i in range(2)]
		self.leds = [LED(i+1, self.output_pins[i]) for i in range(4)]

	def finished_setting_up(self):
		global emu_screen
		emu_screen = self

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

class OutputOverrideSection(gtk.VBox):
	def __init__(self, output_pins):
		gtk.VBox.__init__(self)
		self.output_pins = output_pins
		self.number_of_override_buttons = 8
		widgets = list()

		# main override button
		main_override_btn = gtk.ToggleButton("Override Enable")
		main_override_btn.connect('clicked', self.main_override_clicked)
		main_override_btn.show()
		widgets.append(main_override_btn)

		# pin override buttons
		self.override_buttons = list()
		for i in range(self.number_of_override_buttons):
			new_button = gtk.ToggleButton("Output Pin %d" % (i+1))
			new_button.connect('clicked', self.output_override_clicked, i)
			new_button.show()
			new_button.set_sensitive(False)
			self.override_buttons.append(new_button)
			widgets.append(new_button)

		# all on/off, flip buttons
		self.all_on_btn = gtk.Button("All on")
		self.all_on_btn.connect('clicked', self.all_on_button_clicked)
		self.all_on_btn.set_sensitive(False)
		self.all_on_btn.show()

		self.all_off_btn = gtk.Button("All off")
		self.all_off_btn.connect('clicked', self.all_off_button_clicked)
		self.all_off_btn.set_sensitive(False)
		self.all_off_btn.show()

		self.flip_btn = gtk.Button("Flip")
		self.flip_btn.connect('clicked', self.flip_button_clicked)
		self.flip_btn.set_sensitive(False)
		self.flip_btn.show()

		bottom_button_containter = gtk.HBox()
		bottom_button_containter.pack_start(self.all_on_btn)
		bottom_button_containter.pack_start(self.all_off_btn)
		bottom_button_containter.pack_start(self.flip_btn)
		bottom_button_containter.show()
		widgets.append(bottom_button_containter)

		# pack 'em in
		for widget in widgets:
			self.pack_start(widget)


	"""Callbacks"""
	def main_override_clicked(self, main_override_btn, data=None):
		if main_override_btn.get_active():
			self.enable_override_buttons()
		else:
			self.disable_override_buttons()

	def all_on_button_clicked(self, all_on_btn, data=None):
		for i in range(self.number_of_override_buttons):
			self.override_buttons[i].set_active(True)
			self.output_pins[i].turn_on()

	def all_off_button_clicked(self, all_on_btn, data=None):
		for i in range(self.number_of_override_buttons):
			self.override_buttons[i].set_active(False)
			self.output_pins[i].turn_off()

	def flip_button_clicked(self, flip_btn, data=None):
		for i in range(self.number_of_override_buttons):
			if self.override_buttons[i].get_active():
				self.override_buttons[i].set_active(False)
				self.output_pins[i].turn_off()
			else:
				self.override_buttons[i].set_active(True)
				self.output_pins[i].turn_on()


	def output_override_clicked(self, toggle_button, data=None):
		button_index = data
		self.set_pin(button_index, toggle_button.get_active())


	def set_pin(self, pin_index, pin_value):
		if pin_value:
			self.output_pins[pin_index].turn_on(True)
		else:
			self.output_pins[pin_index].turn_off(True)

	def enable_override_buttons(self):
		self.all_on_btn.set_sensitive(True)
		self.all_off_btn.set_sensitive(True)
		self.flip_btn.set_sensitive(True)
		for i in range(self.number_of_override_buttons):
			self.set_pin(i, self.override_buttons[i].get_active())
			self.override_buttons[i].set_sensitive(True)

	def disable_override_buttons(self):
		# turn off all the pins
		for pin in self.output_pins:
			pin.turn_off(True)

		# disable all of the buttons
		self.all_on_btn.set_sensitive(False)
		self.all_off_btn.set_sensitive(False)
		self.flip_btn.set_sensitive(False)
		for button in self.override_buttons:
			button.set_sensitive(False)


def emu_print(text):
	"""Prints a string with the pfio print prefix"""
	print "%s %s" % (EMU_PRINT_PREFIX, text)
