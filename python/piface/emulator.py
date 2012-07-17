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

#import piface.emulator_parts as emulator_parts
import emulator_parts

import pfio
try:
    pfio.init()
    PFIO_CONNECT = True
except pfio.spi.error:
    print "Could not connect to the SPI module (check privileges)."
    PFIO_CONNECT = False


VERBOSE_MODE = False
DEFAULT_SPACING = 10

EMU_WIDTH  = 292
EMU_HEIGHT = 193
EMU_SPEED  = 20
WINDOW_TITLE = "PiFace Emulator"
emulator_parts.emu_print_PREFIX = "EMU:"

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

# global variables are bad, AND YOU SHOULD FEEL BAD!
rpi_emulator = None
emu_window   = None
emu_screen   = None


class Item(object):
    """An item connected to a pin on the RaspberryPi"""
    def __init__(self, pin_number, is_input=False):
        # an item defaults to an output device
        self.pin_number = pin_number
        self.is_input = is_input

    def _get_value(self):
        return digital_read(self.pin_number)

    def _set_value(self, data):
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


class Emulator(threading.Thread):
    def __init__(self):
        gtk.gdk.threads_init() # init the gdk threads
        threading.Thread.__init__(self)

    def run(self):
        global emu_window
        emu_window = gtk.Window()
        emu_window.connect("delete-event", gtk.main_quit)
        emu_window.set_title(WINDOW_TITLE)

        # emu screen
        global emu_screen
        if PFIO_CONNECT:
            emu_screen = emulator_parts.EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED, pfio)
        else:
            emu_screen = emulator_parts.EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED)

        emu_screen.finished_setting_up()
        emu_screen.show()

        # board connected msg
        if PFIO_CONNECT:
            msg = "Pi Face detected!"
        else:
            msg = "Pi Face not detected"
        board_con_msg = gtk.Label(msg)
        board_con_msg.show()

        # output override section
        output_override_section = \
                emulator_parts.OutputOverrideSection(emu_screen.output_pins)
        output_override_section.show()

        # spi visualiser
        if PFIO_CONNECT:
            spi_visualiser_section = \
                    emulator_parts.SpiVisualiserSection()
            spi_visualiser_section.set_size_request(10, 120)
            spi_visualiser_section.show()

        # vertically pack together the emu_screen and the board connected msg
        container0 = gtk.VBox(homogeneous=False, spacing=DEFAULT_SPACING)
        container0.pack_start(emu_screen)
        container0.pack_start(child=board_con_msg, expand=False)
        container0.show()

        # horizontally pack together the emu screen+msg and the button overide
        container1 = gtk.HBox(homogeneous=True, spacing=DEFAULT_SPACING)
        container1.pack_start(container0)
        container1.pack_start(output_override_section)
        container1.show()
        top_containter = container1

        if PFIO_CONNECT:
            # now, verticaly pack that container and the spi visualiser
            container2 = gtk.VBox(homogeneous=False, spacing=DEFAULT_SPACING)
            container2.pack_start(child=container1, expand=False, fill=False, padding=0)
            container2.pack_start(spi_visualiser_section)
            container2.show()
            top_containter = container2

        emu_window.add(top_containter)
        emu_window.present()
        gtk.main()

"""Input/Output functions mimicing the pfio module"""
def init():
    """Initialises the RaspberryPi emulator"""
    global rpi_emulator
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
    #return 2**(pin_number-1)
    return 1 << (pin_number - 1) # shifting makes more sense
    """
    return pfio.get_pin_bit_mask(pin_number)

def get_pin_number(bit_pattern):
    """Returns the lowest pin number from a given bit pattern"""
    """
    pin_number = 1 # assume pin 1
    while (bit_pattern & 1) == 0:
        bit_pattern = bit_pattern >> 1
        pin_number += 1
        if pin_number > 8:
            pin_number = 0
            break
    
    return pin_number
    """
    return pfio.get_pin_number(bit_pattern)

def build_hex_string(items):
    """Builds a hexidecimal string comprised of the given items"""
    """
    hex_string = ""
    for item in items:
        hex_string += "%02x" % item # 10 = 0a
    return hex_string
    """
    return pfio.build_hex_string(items)

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
    emulator_parts.request_digtial_read = True
    global emu_screen
    value = emu_screen.input_pins[pin_number-1].value
    emulator_parts.request_digtial_read = False
    return value

"""
Some wrapper functions so the user doesn't have to deal with
ugly port variables
"""
def read_output():
    """Returns the values of the output pins"""
    global emu_screen
    return __read_pins(emu_screen.output_pins)

def read_input():
    """Returns the values of the input pins"""
    global emu_screen
    return __read_pins(emu_screen.input_pins)

def __read_pins(pins):
    emulator_parts.request_digtial_read = True
    pin_values = [pin.value for pin in pins]
    data = 0
    for i in range(len(pin_values)):
        data ^= (pin_values[i] & 1) << i
    emulator_parts.request_digtial_read = False
    return data

def write_output(data):
    """Writes the values of the output pins"""
    global emu_screen
    for i in range(8):
        if ((data >> i) & 1) == 1:
            emu_screen.output_pins[i].turn_on()
        else:
            emu_screen.output_pins[i].turn_off()


if __name__ == "__main__":
    init()
