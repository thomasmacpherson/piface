import pygtk
import gtk, gobject, cairo
import threading
from gtk import gdk
from math import pi
from time import sleep
import warnings

import emulator_parts

import pfio
<<<<<<< HEAD
try:
    pfio.init()
    PFIO_CONNECT = True
except pfio.spi.error:
    print "Could not connect to the SPI module (check privileges). Running emulator under the assumption that there is no PiFace."
    PFIO_CONNECT = False
=======
>>>>>>> 17b2bbd88a35a38cbc4447acce3b3196a4762692


VERBOSE_MODE = False
DEFAULT_SPACING = 10

EMU_WIDTH  = 292
EMU_HEIGHT = 193
EMU_SPEED  = 20
WINDOW_TITLE = "PiFace Emulator"

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
pfio_connect = False


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
    def __init__(self, spi_liststore_lock):
        gtk.gdk.threads_init() # init the gdk threads
        threading.Thread.__init__(self)

        # a bit of spaghetti set up
        emulator_parts.pfio = pfio
        emulator_parts.rpi_emulator = self
        self.spi_visualiser_section = emulator_parts.SpiVisualiserFrame(spi_liststore_lock)
        global pfio_connect
        try:
            pfio.init()
            pfio_connect = True
        except pfio.spi.error:
            print "Could not connect to the SPI module (check privileges). Starting emulator assuming that the PiFace is not connected."
            pfio_connect = False
            emulator_parts.pfio = None

        self.emu_window = gtk.Window()
        self.emu_window.connect("delete-event", gtk.main_quit)
        self.emu_window.set_title(WINDOW_TITLE)

        # emu screen
        self.emu_screen = emulator_parts.EmulatorScreen(EMU_WIDTH, EMU_HEIGHT, EMU_SPEED)
        self.emu_screen.show()

        # board connected msg
        if pfio_connect:
            msg = "Pi Face detected!"
        else:
            msg = "Pi Face not detected"
        self.board_con_msg = gtk.Label(msg)
        self.board_con_msg.show()

        if pfio_connect:
            # keep inputs updated
            self.update_input_check = gtk.CheckButton("Keep inputs updated")
            self.update_input_check.show()
            self.update_interval = gtk.Entry(5)
            self.update_interval.set_width_chars(5)
            self.update_interval.set_text("500")
            self.update_interval.show()
            update_interval_label = gtk.Label("ms interval")
            update_interval_label.show()

            self.update_input_check.connect("clicked", self.update_inputs)

            update_inputs_containter = gtk.HBox(False)
            update_inputs_containter.pack_start(self.update_input_check)
            update_inputs_containter.pack_start(self.update_interval, False, False)
            update_inputs_containter.pack_start(update_interval_label, False, False)
            update_inputs_containter.show()

            # spi visualiser checkbox
            self.spi_vis_check = gtk.CheckButton("SPI Visualiser")
            self.spi_vis_check.connect("clicked", self.toggle_spi_visualiser)
            self.spi_vis_check.show()

        # output override section
        self.output_override_section = \
                emulator_parts.OutputOverrideSection(self.emu_screen.output_pins)
        self.output_override_section.show()

        # spi visualiser
        if pfio_connect:
            #spi_visualiser_section = emulator_parts.SpiVisualiserFrame()
            self.spi_visualiser_section.set_size_request(50, 200)
            self.spi_visualiser_section.set_border_width(DEFAULT_SPACING)
            #self.spi_visualiser_section.show()
            self.spi_visualiser_section.hide()

        # vertically pack together the emu_screen and the board connected msg
        container0 = gtk.VBox(homogeneous=False, spacing=DEFAULT_SPACING)
        container0.pack_start(self.emu_screen)
        container0.pack_start(self.board_con_msg)

        if pfio_connect:
            container0.pack_start(update_inputs_containter)
            container0.pack_start(self.spi_vis_check)

        container0.show()

        # horizontally pack together the emu screen+msg and the button overide
        container1 = gtk.HBox(homogeneous=True, spacing=DEFAULT_SPACING)
        container1.pack_start(container0)
        container1.pack_start(self.output_override_section)
        container1.set_border_width(DEFAULT_SPACING)
        container1.show()
        top_containter = container1

        if pfio_connect:
            # now, verticaly pack that container and the spi visualiser
            container2 = gtk.VBox(homogeneous=True, spacing=DEFAULT_SPACING)
            container2.pack_start(child=container1, expand=False, fill=False, padding=0)
            container2.pack_start(self.spi_visualiser_section)
            container2.show()
            top_containter = container2

        self.emu_window.add(top_containter)
        self.emu_window.present()

        self.input_updater = None

    def run(self):
        gtk.main()
    
    def update_inputs(self, widget, data=None):
        """
        If the checkbox has been pressed then schedule the virtual inputs
        to be updated, live
        """
        if widget.get_active():
            self.input_updater = InputUpdater(self.update_interval, self)
            self.input_updater.start()
        else:
            if self.input_updater:
                self.input_updater.stop()
                self.input_updater.join()

    def toggle_spi_visualiser(self, widget, data=None):
        if widget.get_active():
            self.spi_visualiser_section.show()
        else:
            self.spi_visualiser_section.hide()
            self.emu_window.resize(10, 10)

class InputUpdater(threading.Thread):
    def __init__(self, update_interval_entry, rpi_emulator):
        threading.Thread.__init__(self)
        self.update_interval_entry = update_interval_entry
        self.emu = rpi_emulator
        self._stop = threading.Event()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped():
            # get the input pin values
            input_pin_pattern = pfio.read_input()

            # set the virt input pin values
            for i in range(len(self.emu.emu_screen.input_pins)):
                if (input_pin_pattern >> i) & 1 == 1:
                    self.emu.emu_screen.input_pins[i].turn_on(True)
                else:
                    self.emu.emu_screen.input_pins[i].turn_off(True)


            self.emu.emu_screen.queue_draw()

            # sleep
            update_interval = int(self.update_interval_entry.get_text()) / 1000.0
            sleep(update_interval)


"""Input/Output functions mimicing the pfio module"""
def init():
    """Initialises the RaspberryPi emulator"""
    spi_liststore_lock = threading.Semaphore()

    global rpi_emulator
    rpi_emulator = Emulator(spi_liststore_lock)
    rpi_emulator.start()

def deinit():
    """Deinitialises the PiFace"""
    global rpi_emulator
    rpi_emulator.emu_window.destroy()

    gtk.main_quit()

    rpi_emulator.emu_screen = None

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

def hex_cat(items):
    return pfio.hex_cat(items)

def digital_write(pin_number, value):
    """Writes the value given to the pin specified"""
    if VERBOSE_MODE:
        emulator_parts.emu_print("digital write start")

    global rpi_emulator
    if value >= 1:
        rpi_emulator.emu_screen.output_pins[pin_number-1].turn_on()
    else:
        rpi_emulator.emu_screen.output_pins[pin_number-1].turn_off()

    rpi_emulator.emu_screen.queue_draw()

    if VERBOSE_MODE:
        emulator_parts.emu_print("digital write end")

def digital_read(pin_number):
    """Returns the value of the pin specified"""
    emulator_parts.request_digtial_read = True
    global rpi_emulator
    value = rpi_emulator.emu_screen.input_pins[pin_number-1].value
    emulator_parts.request_digtial_read = False

    emu_screen.queue_draw()
    return value

"""
Some wrapper functions so the user doesn't have to deal with
ugly port variables
"""
def read_output():
    """Returns the values of the output pins"""
    global rpi_emulator
    data = __read_pins(rpi_emulator.emu_screen.output_pins)

    global pfio_connect
    if pfio_connect:
        data |= pfio.read_output()

    return data

def read_input():
    """Returns the values of the input pins"""
    global rpi_emulator
    data = __read_pins(rpi_emulator.emu_screen.input_pins)

    global pfio_connect
    if pfio_connect:
        data |= pfio.read_input()
    print "data: %s" % data
    return data

def __read_pins(pins):
    vpin_values = [pin._value for pin in pins]
    data = 0
    for i in range(len(vpin_values)):
        data ^= (vpin_values[i] & 1) << i
    
    #global rpi_emulator
    #rpi_emulator.emu_screen.queue_draw()

    return data

def write_output(data):
    """Writes the values of the output pins"""
    global rpi_emulator
    for i in range(8):
        if ((data >> i) & 1) == 1:
            rpi_emulator.emu_screen.output_pins[i].turn_on()
        else:
            rpi_emulator.emu_screen.output_pins[i].turn_off()

    rpi_emulator.emu_screen.queue_draw()


if __name__ == "__main__":
    init()
