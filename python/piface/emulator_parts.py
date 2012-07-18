import pygtk
pygtk.require("2.0")
import gtk, gobject, cairo
from math import pi

TESTING = False

# relative directories
VIRT_PI_IMAGE = "images/pi.png"
VIRT_LED_ON_IMAGE = "images/led_on.png"
if not TESTING:
    import os.path, sys
    package_dir = os.path.dirname(sys.modules["piface"].__file__)
    VIRT_PI_IMAGE = os.path.join(package_dir, VIRT_PI_IMAGE)
    VIRT_LED_ON_IMAGE = os.path.join(package_dir, VIRT_LED_ON_IMAGE)

EMU_PRINT_PREFIX = "EMU:"

PIN_COLOUR_RGB = (0, 1, 1)

MAX_SPI_LOGS = 50

DEFAULT_SPACING = 10

# pin circle locations
ledsX = [180.7, 180.7, 236.7, 219.1]
ledsY = [131.3, 72.3, 22.2, 22.2]
switchesX = [14.3, 39.3, 64.3, 89.3]
switchesY = [157.5, 157.5, 157.5, 157.5]
relay1VirtPinsX = [285.0,285.0,285.0]
relay1VirtPinsY = [124.0,136.0,148.0]
relay2VirtPinsX = [285.0,285.0,285.0,]
relay2VirtPinsY = [73.0,86.0,98.0]
boardInputVirtPinsX = [6.0,19.0,31.0,44.0,56.0,68.0,80.0,92.0,104]
boardInputVirtPinsY = [186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0,186.0]
"""
# 1 -> 9
boardOutputVirtPinsX = [181.0,194.0,206.0,218.0,230.0,242.0,254.0,266.0,278.0]
boardOutputVirtPinsY = [8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0,8.0]
"""
# 8 <- 1
boardOutputVirtPinsX = [266.0, 254.0, 242.0, 230.0, 218.0, 206.0, 194.0, 181.0]
boardOutputVirtPinsY = [8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0, 8.0]

RELAY_PIN_PATTERN_ON  = (0, 1, 1)
RELAY_PIN_PATTERN_OFF = (1, 1, 0)

# piface peripheral pin numbers
# each peripheral is connected to an I/O pin
# some pins are connected to many peripherals
# outputs
PH_PIN_VirtLED_1 = 1
PH_PIN_VirtLED_2 = 2
PH_PIN_VirtLED_3 = 3
PH_PIN_VirtLED_4 = 4
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

# don't update the input pins unless the user makes a digital read
# this is because an update is requested on every single mouse move
# which creates a TON of SPI traffic. Turn this to True if you want
# a full emulator mimic of the board (including inputs).
request_digtial_read = False


class VirtItem(object):
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
        global request_digtial_read
        if pfio and self.is_input and request_digtial_read:
            real_pin_value = pfio.digital_read(self.pin_number)
            print "readign"
            if real_pin_value == 1:
                return real_pin_value

        return self._value

    def _set_value(self, new_value):
        if not self._hold or (self._hold and self._force):
            self._value = new_value
            self._hold  = False
            self._force = False

            """
            global emu_screen
            if emu_screen:
                pass
                emu_screen.queue_draw()
            """

            global pfio
            if pfio and not self.is_input and not self.is_relay_ext_pin:
                # update the state of the actual output devices
                pfio.digital_write(self.pin_number, new_value)
                #print "Setting pin %d to %d" % (self.pin_number, new_value
                
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
                self.attached_pin = VirtPin(pin_number)
            else:
                self.attached_pin = VirtPin(pin_number)

class VirtPin(VirtItem):
    def __init__(self, pin_number, is_input=False,
            is_relay1_pin=False, is_relay2_pin=False,
            is_relay_ext_pin=False):
        if is_relay1_pin:
            self.x = relay1VirtPinsX[pin_number]
            self.y = relay1VirtPinsY[pin_number]
        elif is_relay2_pin:
            self.x = relay2VirtPinsX[pin_number]
            self.y = relay2VirtPinsY[pin_number]
        elif is_input:
            self.x = boardInputVirtPinsX[pin_number-1]
            self.y = boardInputVirtPinsY[pin_number-1]
        else:
            self.x = boardOutputVirtPinsX[pin_number-1]
            self.y = boardOutputVirtPinsY[pin_number-1]

        VirtItem.__init__(self, pin_number, is_input, is_relay_ext_pin)

    def draw_hidden(self, cr):
        cr.arc(self.x, self.y, 5, 0, 2*pi)

    def draw(self, cr):
        if self.value == 1:
            #print "drawing pin at %d, %d" % (self.x, self.y)
            cr.save()
            pin_colour_r, pin_colour_g, pin_colour_b = PIN_COLOUR_RGB
            cr.set_source_rgb(pin_colour_r, pin_colour_g, pin_colour_b)
            cr.arc (self.x, self.y, 5, 0, 2*pi);
            cr.fill()
            cr.restore()

class VirtLED(VirtItem):
    """A virtual VirtLED on the RaspberryPi emulator"""
    def __init__(self, led_number, attached_pin=None):
        self.attach_pin(attached_pin, led_number)

        self.x = ledsX[led_number-1]
        self.y = ledsY[led_number-1]

        VirtItem.__init__(self, led_number)

    def _get_value(self):
        return self.attached_pin.value

    def _set_value(self, new_value):
        self.attached_pin.value = new_value
    
    value = property(_get_value, _set_value)

    def turn_on(self):
        #print "turning on VirtLED"
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
                # draw the illuminated VirtLED
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

class VirtRelay(VirtItem):
    """A relay on the RaspberryPi"""
    def __init__(self, relay_number, attached_pin=None):
        self.attach_pin(attached_pin, relay_number)

        if relay_number == 1:
            self.pins = [VirtPin(i, False, True, False, True) for i in range(3)]
        else:
            self.pins = [VirtPin(i, False, False, True, True) for i in range(3)]

        VirtItem.__init__(self, relay_number)

        #self.value = self.attached_pin.value

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

class VirtSwitch(VirtItem):
    """A virtual switch on the RaspberryPi emulator"""
    def __init__(self, switch_number, attached_pin=None):
        self.attach_pin(attached_pin, switch_number, True)

        self.x = switchesX[switch_number-1]
        self.y = switchesY[switch_number-1]
        VirtItem.__init__(self, switch_number, True)

    def _get_value(self):
        return self.attached_pin.value

    def _set_value(self, new_value):
        self.attached_pin.value = new_value
    
    value = property(_get_value, _set_value)

    def turn_on(self):
        self.value = 1;
    
    def turn_off(self):
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
        self.queue_draw()

    def _button_press(self, widget, event):
        self.x = event.x
        self.y = event.y
        self.button_pressed = True
        self.queue_draw()

class EmulatorScreen(Screen):
    """This class is also a Drawing Area, coming from Screen."""
    def __init__ (self, w, h, speed):
        Screen.__init__(self, w, h, speed)

        global have_led_image
        try:
            f = open(VIRT_LED_ON_IMAGE)
            f.close()
            have_led_image = True
        except:
            emu_print("could not find the virtual led image: %s" % VIRT_LED_ON_IMAGE)
            have_led_image = False

        self.input_pins = [VirtPin(i, True) for i in range(1,9)]
        self.switches = [VirtSwitch(i+1, self.input_pins[i]) for i in range(4)]

        self.output_pins = [VirtPin(i) for i in range(1,9)]
        self.relays = [VirtRelay(i+1, self.output_pins[i]) for i in range(2)]
        self.leds = [VirtLED(i+1, self.output_pins[i]) for i in range(4)]

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
            pin.draw_hidden(cr) # perhaps this is where the heavy traffic is
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

    def update_voutput_pins(self):
        """
        Updates the state of each virtual output pin to match
        that of the real pins
        """
        if not pfio:
            raise Exception(
                    "Looks like some sloppy programmer (probably Tom Preston...) " \
                    "is trying to update the virtual output pins when the PiFace " \
                    "isn't connected. Make sure you check for the pfio before calling " \
                    "the update_voutput_pins method. kthxbai.")

        output_bit_map = pfio.read_output()
        for i in range(len(self.output_pins)):
            # updating inner value so that we don't do more SPI reads
            self.output_pins[i]._value = (output_bit_map >> i) & 1 

        self.queue_draw()

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

        self.batch_button = False

    """Callbacks"""
    def main_override_clicked(self, main_override_btn, data=None):
        if main_override_btn.get_active():
            self.enable_override_buttons()
        else:
            self.disable_override_buttons()

        global emu_screen
        emu_screen.queue_draw()

    def all_on_button_clicked(self, all_on_btn, data=None):
        self.batch_button = True
        for i in range(self.number_of_override_buttons):
            self.override_buttons[i].set_active(True)
            self.output_pins[i]._value = 1

        self.set_pins()

        global emu_screen
        emu_screen.queue_draw()

        self.batch_button = False

    def all_off_button_clicked(self, all_on_btn, data=None):
        self.batch_button = True

        for i in range(self.number_of_override_buttons):
            self.override_buttons[i].set_active(False)
            self.output_pins[i]._value = 0

        self.set_pins()

        global emu_screen
        emu_screen.queue_draw()

        self.batch_button = False

    def flip_button_clicked(self, flip_btn, data=None):
        self.batch_button = True
        for i in range(self.number_of_override_buttons):
            if self.override_buttons[i].get_active():
                self.override_buttons[i].set_active(False)
                self.output_pins[i]._value = 0
            else:
                self.override_buttons[i].set_active(True)
                self.output_pins[i]._value = 1

        self.set_pins()
        global emu_screen
        emu_screen.queue_draw()

        self.batch_button = False

    def output_override_clicked(self, toggle_button, data=None):
        if not self.batch_button:
            self.set_pins()

    def set_pins(self):
        global emu_screen
        pin_bit_mask = 0 # for the pfio
        for i in range(len(self.override_buttons)):
            if self.override_buttons[i].get_active():
                pin_bit_mask ^= 1 << i
                emu_screen.output_pins[i]._value = 1
            else:
                pin_bit_mask ^= 0 << i
                emu_screen.output_pins[i]._value = 0

        global pfio
        if pfio:
            pfio.write_output(pin_bit_mask)

        emu_screen.queue_draw()

    def enable_override_buttons(self):
        self.all_on_btn.set_sensitive(True)
        self.all_off_btn.set_sensitive(True)
        self.flip_btn.set_sensitive(True)
        for i in range(self.number_of_override_buttons):
            self.override_buttons[i].set_sensitive(True)

        self.set_pins()

        global emu_screen
        emu_screen.queue_draw()

    def disable_override_buttons(self):
        # turn off all the pins
        for pin in self.output_pins:
            pin._value = 0
        global pfio
        if pfio:
            pfio.write_output(0)

        # disable all of the buttons
        self.all_on_btn.set_sensitive(False)
        self.all_off_btn.set_sensitive(False)
        self.flip_btn.set_sensitive(False)
        for button in self.override_buttons:
            button.set_sensitive(False)

        global emu_screen
        emu_screen.queue_draw()

class SpiVisualiserFrame(gtk.Frame):
    def __init__(self):
        gtk.Frame.__init__(self, "SPI Visualiser")
        container = gtk.VBox(False)

        spi_visualiser_section = SpiVisualiserSection()
        spi_visualiser_section.show()
        container.pack_start(child=spi_visualiser_section, expand=True, fill=True)

        spi_sender_section = SpiSenderSection()
        spi_sender_section.show()
        container.pack_end(child=spi_sender_section, expand=False)

        container.show()
        container.set_border_width(DEFAULT_SPACING)
        self.add(container)
        self.set_border_width(DEFAULT_SPACING)
        self.show()

class SpiVisualiserSection(gtk.ScrolledWindow):
    def __init__(self):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        # create a liststore with three string columns to use as the model
        self.liststore = gtk.ListStore(str, str, str, str, str)
        self.liststoresize = 0
        
        global pfio
        if pfio:
            pfio.spi_visualiser_section = self

        # create the TreeView using liststore
        self.treeview = gtk.TreeView(self.liststore)
        self.treeview.connect('size-allocate', self.treeview_changed)

        # create the TreeViewColumns to display the data
        self.tvcolumn = (gtk.TreeViewColumn('Time'),
                gtk.TreeViewColumn('In'),
                gtk.TreeViewColumn('In Breakdown'),
                gtk.TreeViewColumn('Out'),
                gtk.TreeViewColumn('Out Breakdown'))

        # add columns to treeview
        for column in self.tvcolumn:
            self.treeview.append_column(column)

        # create a CellRenderers to render the data
        self.cell = [gtk.CellRendererText() for i in range(5)]

        # set background color property
        self.cell[0].set_property('cell-background', 'cyan')
        self.cell[1].set_property('cell-background', '#87ea87')
        self.cell[2].set_property('cell-background', '#98fb98')
        self.cell[3].set_property('cell-background', '#ffccbb')
        self.cell[4].set_property('cell-background', '#ffddcc')

        # add the cells to the columns
        for i in range(len(self.tvcolumn)):
            self.tvcolumn[i].pack_start(self.cell[i], True)

        for i in range(len(self.tvcolumn)):
            self.tvcolumn[i].set_attributes(self.cell[i], text=i)

        # make treeview searchable
        self.treeview.set_search_column(0)

        # Allow sorting on the column
        self.tvcolumn[0].set_sort_column_id(0)

        # Allow drag and drop reordering of rows
        self.treeview.set_reorderable(True)

        self.add(self.treeview)
        self.treeview.show()

    def treeview_changed(self, widget, event, data=None):
        adjustment = self.get_vadjustment()
        adjustment.set_value(adjustment.upper - adjustment.page_size)

    def add_spi_log(self, time, data_tx, data_rx):
        if self.liststoresize >= MAX_SPI_LOGS:
            #remove the first item
            first_row_iter = self.treeview.get_model()[0].iter
            self.liststore.remove(first_row_iter)
        else:
            self.liststoresize += 1

        data_tx_breakdown = self.get_data_breakdown(data_tx)
        data_rx_breakdown = self.get_data_breakdown(data_rx)
        self.liststore.append((time, "0x%06x" % data_tx, data_tx_breakdown, "0x%06x" % data_rx, data_rx_breakdown))
        
    def get_data_breakdown(self, raw_data):
        cmd = (raw_data >> 16) & 0xff
        if cmd == pfio.WRITE_CMD:
            cmd = "WRITE"
        elif cmd == pfio.READ_CMD:
            cmd = "READ"
        else:
            cmd = hex(cmd)

        port = (raw_data >> 8) & 0xff
        if port == pfio.IODIRA:
            port = "IODIRA"
        elif port == pfio.IODIRB:
            port = "IODIRB"
        elif port == pfio.IOCON:
            port = "IOCON"
        elif port == pfio.GPIOA:
            port = "GPIOA"
        elif port == pfio.GPIOB:
            port = "GPIOB"
        elif port == pfio.GPPUA:
            port = "GPPUA"
        elif port == pfio.GPPUB:
            port = "GPPUB"
        else:
            port = hex(port)

        data = hex(raw_data & 0xff)

        data_breakdown = "cmd: %s, port: %s, data: %s" % (cmd, port, data)
        return data_breakdown

class SpiSenderSection(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self, False)

        label = gtk.Label("SPI Input: ")
        label.show()

        self.spi_input = gtk.Entry()
        self.spi_input.set_text("0x0")
        self.spi_input.show()

        button = gtk.Button("Send")
        button.connect("clicked", self.send_spi_message)
        button.show()

        self.error_label = gtk.Label()
        self.error_label.show()

        self.pack_start(child=label, expand=False)
        self.pack_start(child=self.spi_input, expand=False)
        self.pack_start(child=button, expand=False)
        self.pack_start(child=self.error_label, expand=False)

    def __set_error_label_text(self, text):
        self.__error_text = text
        self.error_label.set_markup("<span foreground='#ff0000'> %s</span>" % self.__error_text)

    def __get_error_label_text(self):
        return self.__error_text
    
    error_text = property(__get_error_label_text, __set_error_label_text)

    def send_spi_message(self, widget, data=None):
        self.error_text = ""
        spi_message = 0
        user_input = self.spi_input.get_text()
        try:
            if "0x" == user_input[:2]:
                spi_message = int(user_input, 16)
            elif "0b"== user_input[:2]:
                spi_message = int(user_input, 2)
            else:
                spi_message = int(user_input)

            # check we are three bytes long
            if len(hex(spi_message)[2:]) > 6:
                raise ValueError()

        except ValueError:
            msg = "Invalid SPI message"
            self.error_text = msg
            print msg
            return


        cmd  = (spi_message >> 16) & 0xff
        port = (spi_message >> 8) & 0xff
        data = (spi_message) & 0xff
        pfio.send([(cmd, port, data)])

        emu_screen.update_voutput_pins()


def emu_print(text):
    """Prints a string with the pfio print prefix"""
    print "%s %s" % (EMU_PRINT_PREFIX, text)
