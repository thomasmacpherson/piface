"""
pfion.py
A network version of the pfio - can talk to Pi Face's over a network
"""
import socket
import threading
import struct
import pfio


DEFAULT_PORT = 15432
BUFFER_SIZE  = 100

UNKNOWN_CMD   = 0
WRITE_OUT_CMD = 1
WRITE_OUT_ACK = 2
READ_OUT_CMD  = 3
READ_OUT_ACK  = 4
READ_IN_CMD   = 5
READ_IN_ACK   = 6
DIGITAL_WRITE_CMD = 7
DIGITAL_WRITE_ACK = 8
DIGITAL_READ_CMD  = 9
DIGITAL_READ_ACK  = 10

STRUCT_UNIT_TYPE = "B"

"""
# testing without pfio
outpins = 0
inpins = 0
def fakepfioinit():
    pass
def fakepfiowrite(something):
    print "writing ", something
    global outpins
    outpins = something
def fakepfioreadin():
    print "read in"
    return 0b10101010
def fakepfioreadout():
    print "read out"
    global outpins
    return outpins
pfio.init = fakepfioinit
pfio.write_output = fakepfiowrite
pfio.read_input = fakepfioreadin
pfio.read_output = fakepfioreadout
"""


class UnknownPacketReceivedError(Exception):
    pass


class PfionPacket(object):
    """Models a Pfio network packet"""
    def __init__(self, command=UNKNOWN_CMD):
        self.command  = command
        self.cmd_data = 0  # 1 byte of data associated with the cmd
        self.data     = "" # extra data as a string

    def for_network(self):
        """Returns this pfion packet as a struct+data"""
        pcmddata = struct.pack(STRUCT_UNIT_TYPE*2, self.command, self.cmd_data)
        return  pcmddata + self.data

    def from_network(self, raw_struct):
        """Returns this pfion packet with new values interpereted from
        the struct+data given in"""
        self.command,  = struct.unpack(STRUCT_UNIT_TYPE, raw_struct[0])
        self.cmd_data, = struct.unpack(STRUCT_UNIT_TYPE, raw_struct[1])
        self.data = raw_struct[2:]
        return self

    """Pin number and pin value are stored in the upper and lower
    nibbles of the first data byte respectively. These are for digital
    read and digital write operations"""
    def _get_pin_number(self):
        return self.cmd_data >> 4

    def _set_pin_number(self, new_pin_number):
        self.cmd_data = (new_pin_number << 4) ^ (self.cmd_data & 0xf)

    pin_number = property(_get_pin_number, _set_pin_number)

    def _get_pin_value(self):
        return self.cmd_data & 0xf

    def _set_pin_value(self, new_pin_value):
        self.cmd_data = (new_pin_value & 0xf) ^ (self.cmd_data & 0xf0)

    pin_value = property(_get_pin_value, _set_pin_value)

    def _get_bit_pattern(self):
        return self.cmd_data

    def _set_bit_pattern(self, new_bit_pattern):
        self.cmd_data = new_bit_pattern & 0xff

    bit_pattern = property(_get_bit_pattern, _set_bit_pattern)

class PfioWorker(threading.Thread):
    def __init__(self, pfio_socket, src_addr, connection_number):
        print "Initialising connection %s from %s" % (connection_number, src_addr)
        threading.Thread.__init__(self)
        self.pfio_socket = pfio_socket
        self.connection_number = connection_number
        self.src_addr = src_addr

    def run(self):
        self.pfio_socket.close()


def start_pfio_server(callback=None, verbose=False, port=DEFAULT_PORT):
    """Starts listening for pfio packets over the network"""
    pfio.init()
    try:
        hostname = socket.gethostname()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind((hostname, port))
    except socket.error as e:
        print "There was an error setting up the server socket!"
        print e
        return
    else:
        if verbose:
            print "Listening at %s on port %d" % (hostname, port)

    while True:
        # get the packet
        packet, sender = sock.recvfrom(BUFFER_SIZE)
        if verbose:
            print "Recieved packet from", sender
        # make it something sensible
        packet = PfionPacket().from_network(packet)

        if packet.command == WRITE_OUT_CMD:
            pfio.write_output(packet.bit_pattern)
            p = PfionPacket(WRITE_OUT_ACK)
            sock.sendto(p.for_network(), sender)

        elif packet.command == READ_OUT_CMD:
            output_bitp = pfio.read_output()
            p = PfionPacket(READ_OUT_ACK)
            p.bit_pattern = output_bitp
            sock.sendto(p.for_network(), sender)

        elif packet.command == READ_IN_CMD:
            input_bitp = pfio.read_input()
            p = PfionPacket(READ_IN_ACK)
            p.bit_pattern = input_bitp
            sock.sendto(p.for_network(), sender)

        elif packet.command == DIGITAL_WRITE_CMD:
            pfio.digital_write(packet.pin_number, packet.pin_value)
            p = PfionPacket(DIGITAL_WRITE_ACK)
            sock.sendto(p.for_network(), sender)

        elif packet.command ==  DIGITAL_READ_CMD:
            pin_value = pfio.digital_read(packet.pin_number)
            p = PfionPacket(DIGITAL_READ_ACK)
            p.pin_number = packet.pin_number
            p.pin_value  = pin_value
            sock.sendto(p.for_network(), sender)

        elif callback != None:
            callback(packet)

        elif verbose:
            print "Unkown packet command (%d). Ignoring." % packet.command

# sending functions
def send_packet(packet, hostname, port=DEFAULT_PORT):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(packet.for_network(), (hostname, port))
    return sock

def send_write_output(output_bitp, hostname, port=DEFAULT_PORT):
    packet = PfionPacket(WRITE_OUT_CMD)
    packet.bit_pattern = output_bitp
    sock = send_packet(packet, hostname)
    p, sender = sock.recvfrom(BUFFER_SIZE)
    packet = PfionPacket().from_network(p)
    if packet.command != WRITE_OUT_ACK:
        raise UnknownPacketReceivedError(
                "Received packet command (%d) was not WRITE_OUT_ACK" %
                packet.command)

def send_read_output(hostname, port=DEFAULT_PORT):
    packet = PfionPacket(READ_OUT_CMD)
    sock = send_packet(packet, hostname)
    p, sender = sock.recvfrom(BUFFER_SIZE)
    packet = PfionPacket().from_network(p)
    if packet.command == READ_OUT_ACK:
        return packet.bit_pattern
    else:
        raise UnknownPacketReceivedError(
                "Received packet command (%d) was not READ_OUT_ACK" %
                packet.command)

def send_read_input(hostname, port=DEFAULT_PORT):
    packet = PfionPacket(READ_IN_CMD)
    sock = send_packet(packet, hostname)
    p, sender = sock.recvfrom(BUFFER_SIZE)
    packet = PfionPacket().from_network(p)
    if packet.command == READ_IN_ACK:
        return packet.bit_pattern
    else:
        raise UnknownPacketReceivedError(
                "Received packet command (%d) was not READ_IN_ACK" %
                packet.command)

def send_digital_write(pin_number, pin_value, hostname, port=DEFAULT_PORT):
    packet = PfionPacket(DIGITAL_WRITE_CMD)
    packet.pin_number = pin_number
    packet.pin_value = pin_value
    sock = send_packet(packet, hostname)
    p, sender = sock.recvfrom(BUFFER_SIZE)
    packet = PfionPacket().from_network(p)
    if packet.command != DIGITAL_WRITE_ACK:
        raise UnknownPacketReceivedError(
                "Received packet command (%d) was not DIGITAL_WRITE_ACK" %
                packet.command)

def send_digital_read(pin_number, hostname, port=DEFAULT_PORT):
    packet = PfionPacket(DIGITAL_READ_CMD)
    packet.pin_number = pin_number
    sock = send_packet(packet, hostname)
    p, sender = sock.recvfrom(BUFFER_SIZE)
    packet = PfionPacket().from_network(p)
    if packet.command == DIGITAL_READ_ACK:
        return packet.pin_value
    else:
        raise UnknownPacketReceivedError(
                "Received packet command (%d) was not DIGITAL_READ_ACK" %
                packet.command)
