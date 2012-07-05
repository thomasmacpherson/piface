from array import array
import socket
import time
import sys

from Tkinter import Tk
from tkSimpleDialog import askstring
root = Tk()
root.withdraw()

PORT = 42001
HOST = askstring('Scratch Connector', 'IP:')

def send_scratch_command(cmd):
	n = len(cmd)
	a = array('c')
	a.append(chr((n >> 24) & 0xFF))
	a.append(chr((n >> 16) & 0xFF))
	a.append(chr((n >>  8) & 0xFF))
	a.append(chr(n & 0xFF))
	scratch_sock.send(a.tostring() + cmd)

if __name__ == "__main__":
	if not HOST:
		sys.exit()

	print 'Connecting...'
	scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	scratch_sock.connect((HOST, PORT))
	print 'Connected!'

	while True:
		msg = askstring('Scratch Connector', 'Send Broadcast:')
		if msg:
			send_scratch_command('broadcast "' + msg + '"')
from array import array
import struct
import socket
import time
import sys

from Tkinter import Tk
from tkSimpleDialog import askstring
root = Tk()
root.withdraw()

PORT = 42001
HOST = askstring('Scratch Connector', 'IP:')
#HOST = "130.88.194.67"

def receive_scratch_broadcast():
	data = scratch_sock.recv(100)
	length = struct.unpack(">i", "%c%c%c%c" % (data[0], data[1], data[2], data[3]))[0]
	print "length: %s" % length
	print "data: %s" % data[4:]

if __name__ == "__main__":
	if not HOST:
		sys.exit()

	print 'Connecting...'
	scratch_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	scratch_sock.connect((HOST, PORT))
	print 'Connected!'

	while True:
		receive_scratch_broadcast()
