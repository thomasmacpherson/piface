"""
spivisualiser.py
An SPI visualiser for sending SPI packets to the SPI port
"""
import pygtk
pygtk.require("2.0")
import gtk

class SpiVisualiserSection(gtk.ScrolledWindow):
    def __init__(self, liststore_lock):
        gtk.ScrolledWindow.__init__(self)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)

        self.liststore_lock = liststore_lock

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

    def add_spi_log(self, time, data_tx, data_rx, custom_spi=False):
        if self.liststoresize >= MAX_SPI_LOGS:
            #remove the first item
            first_row_iter = self.treeview.get_model()[0].iter
            self.liststore.remove(first_row_iter)
        else:
            self.liststoresize += 1

        data_tx_breakdown = self.get_data_breakdown(data_tx)
        data_rx_breakdown = self.get_data_breakdown(data_rx)

        if custom_spi:
            in_fmt = "[0x%06x]" # use a special format
        else:
            in_fmt = "0x%06x"

        out_fmt = "0x%06x"

        data_tx_str = in_fmt  % data_tx
        data_rx_str = out_fmt % data_rx

        self.liststore_lock.acquire()
        self.liststore.append((time, data_tx_str, data_tx_breakdown, data_rx_str, data_rx_breakdown))
        self.liststore_lock.release()
        
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

        self.update_emu_button = gtk.Button("Update Emulator")
        self.update_emu_button.connect("clicked", self.update_emu_button_pressed)
        self.update_emu_button.show()

        self.pack_start(child=label, expand=False)
        self.pack_start(child=self.spi_input, expand=False)
        self.pack_start(child=button, expand=False)
        self.pack_start(child=self.error_label, expand=False)
        self.pack_end(child=self.update_emu_button, expand=False)

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
        pfio.send([(cmd, port, data)], True)

    def update_emu_button_pressed(self, widget, data=None):
        global rpi_emulator
        rpi_emulator.output_override_section.reset_buttons()
        rpi_emulator.emu_screen.update_voutput_pins()
