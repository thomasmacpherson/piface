from array import array
import threading
import socket
import time
import sys
import struct

from Tkinter import Tk
from tkSimpleDialog import askstring
root = Tk()
root.withdraw()

PORT = 42001
HOST = '130.88.194.67'
#HOST = askstring('Scratch Connector', 'IP:')
BUFFER_SIZE = 100

SCRATCH_SENSOR_NAME_INPUT_1 = "piface-input1"
SCRATCH_SENSOR_NAME_INPUT_2 = "piface-input2"
SCRATCH_SENSOR_NAME_INPUT_3 = "piface-input3"
SCRATCH_SENSOR_NAME_INPUT_4 = "piface-input4"
SCRATCH_SENSOR_NAME_INPUT_5 = "piface-input5"
SCRATCH_SENSOR_NAME_INPUT_6 = "piface-input6"
SCRATCH_SENSOR_NAME_INPUT_7 = "piface-input7"
SCRATCH_SENSOR_NAME_INPUT_8 = "piface-input8"


class ScratchSender(threading.Thread):
	def __init__(self, socket):
		threading.Thread.__init__(self)
		self.scratch_socket = socket

	def run(self):
		last_bit_pattern = 0b0
		while True:
			pin_bit_pattern = pfio.read_input()[2]
			msg = askstring('Scratch Connector', 'Send Broadcast:')
			if msg:
				#self.send_scratch_command('broadcast "' + msg + '"')
				self.send_scratch_command('sensor-update "slider" 1')

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

	def run(self):
		while True:
			try:
				data = self.scratch_socket.recv(BUFFER_SIZE)
				length = struct.unpack(
						'>i',
						'%c%c%c%c' % (data[0], data[1], data[2], data[3])
					)[0]
				print 'Recieved data from Scratch!'
				print 'Length: %d, Data: %s' % (length, data[4:])
				print data[4:].split(" ")
				print ""
			except: # TODO: specify and error here
				break


def create_socket(host, port):
	scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	scratch_sock.connect((host, port))
	return scratch_sock

if __name__ == '__main__':
	if not HOST:
		sys.exit()

	# open the socket
	print 'Connecting...' ,
	socket = create_socket(HOST, PORT)
	print 'Connected!'

	listener = ScratchListener(socket)
	sender = ScratchSender(socket)
	listener.start()
	sender.start()
