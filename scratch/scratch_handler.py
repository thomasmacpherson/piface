from array import array
import threading
import socket
import time
import sys
import struct

if "-e" in sys.argv:
    import piface.emulator as pfio
    sys.argv.remove("-e")
else:
    import piface.pfio as pfio

PORT = 42001
DEFAULT_HOST = '127.0.0.1'
BUFFER_SIZE = 100
SOCKET_TIMEOUT = 1

SCRATCH_SENSOR_NAME_INPUT = (
    'piface-input1',
    'piface-input2',
    'piface-input3',
    'piface-input4',
    'piface-input5',
    'piface-input6',
    'piface-input7',
    'piface-input8')

SCRATCH_SENSOR_NAME_OUTPUT = (
    'piface-output1',
    'piface-output2',
    'piface-output3',
    'piface-output4',
    'piface-output5',
    'piface-output6',
    'piface-output7',
    'piface-output8')


class ScratchSender(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.scratch_socket = socket
        self._stop = threading.Event()

        # make scratch aware of the pins
        for i in range(len(SCRATCH_SENSOR_NAME_INPUT)):
            self.broadcast_pin_update(i, 0)

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        last_bit_pattern = 0
        while not self.stopped():
            pin_bit_pattern = pfio.read_input()

            # if there is a change in the input pins
            changed_pins = pin_bit_pattern ^ last_bit_pattern
            if changed_pins:
                try:
                    self.broadcast_changed_pins(changed_pins, pin_bit_pattern)
                except Exception as e:
                    print e
                    break

            last_bit_pattern = pin_bit_pattern

    def broadcast_changed_pins(self, changed_pin_map, pin_value_map):
        for i in range(8):
            # if we care about this pin's value
            if (changed_pin_map >> i) & 0b1:
                pin_value = (pin_value_map >> i) & 0b1
                self.broadcast_pin_update(i, pin_value)

    def broadcast_pin_update(self, pin_index, value):
        sensor_name = SCRATCH_SENSOR_NAME_INPUT[pin_index]
        bcast_str = 'sensor-update "%s" %d' % (sensor_name, value)
        print 'sending: %s' % bcast_str
        self.send_scratch_command(bcast_str)

    def send_scratch_command(self, cmd):
        n = len(cmd)
        a = array('c')
        a.append(chr((n >> 24) & 0xFF))
        a.append(chr((n >> 16) & 0xFF))
        a.append(chr((n >>  8) & 0xFF))
        a.append(chr(n & 0xFF))
        self.scratch_socket.send(a.tostring() + cmd)

class ScratchListener(threading.Thread):
    def __init__(self, socket):
        threading.Thread.__init__(self)
        self.scratch_socket = socket
        self._stop = threading.Event()

        self.last_zero_bit_mask = 0
        self.last_one_bit_mask  = 0

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

    def run(self):
        while not self.stopped():
            try:
                data = self.scratch_socket.recv(BUFFER_SIZE)
                #length = struct.unpack(
                #        '>i',
                #        '%c%c%c%c' % (data[0], data[1], data[2], data[3])
                #    )[0]
                data = data[4:] # get rid of the length info
                #print 'Length: %d, Data: %s' % (length, data)

            except socket.timeout: # if we timeout, re-loop
                continue
            except: # exit on any other errrors
                break

            data = data.split(" ")
            
            if data[0] == 'sensor-update':
                data = data[1:]
                print 'received sensor-update:', data
                self.sensor_update(data)
                    
            elif data[0] == 'broadcast':
                data = data[1:]
                print 'received broadcast:', data

            else:
                print 'received something:', data

    def sensor_update(self, data):
        index_is_data = False # ignore the loop contents if not sensor
        zero_bit_mask = 0 # bit mask showing where zeros should be written
        one_bit_mask  = 0 # bit mask showing where ones should be written
        we_should_update_piface = False

        # go through all of the sensors that have been updated
        for i in range(len(data)):

            if index_is_data:
                index_is_data = False
                continue

            sensor_name = data[i].strip('"')
            
            # if this sensor is a piface output then reflect
            # that update on the board
            if sensor_name in SCRATCH_SENSOR_NAME_OUTPUT:
                we_should_update_piface = True
                pin_index = SCRATCH_SENSOR_NAME_OUTPUT.index(sensor_name)
                sensor_value = int(data[i+1])
                index_is_data = True

                # could this be made more efficient by sending a single write
                if sensor_value == 0:
                    zero_bit_mask ^= (1 << pin_index)

                else:
                    one_bit_mask ^= (1 << pin_index)

        if we_should_update_piface:
            old_pin_bitp = pfio.read_output() # grab the old values
            new_pin_bitp = old_pin_bitp & ~zero_bit_mask # set the zeros
            new_pin_bitp |= one_bit_mask # set the ones

            if new_pin_bitp != old_pin_bitp:
                pfio.write_output(new_pin_bitp) # write the new bit pattern


def create_socket(host, port):
    try:
        scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        scratch_sock.connect((host, port))
    except socket.error:
        print "There was an error connecting to Scratch!"
        print "I couldn't find a Mesh session at host: %s, port: %s" % (host, port) 
        sys.exit(1)

    return scratch_sock

def cleanup_threads(threads):
    for thread in threads:
        thread.stop()

    for thread in threads:
        thread.join()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = DEFAULT_HOST

    # open the socket
    print 'Connecting...' ,
    the_socket = create_socket(host, PORT)
    print 'Connected!'

    the_socket.settimeout(SOCKET_TIMEOUT)

    pfio.init()

    listener = ScratchListener(the_socket)
    sender = ScratchSender(the_socket)
    listener.start()
    sender.start()

    # wait for ctrl+c
    try:
        while True:
            pass
    except KeyboardInterrupt:
        cleanup_threads((listener, sender))
        pfio.deinit()
        sys.exit()
