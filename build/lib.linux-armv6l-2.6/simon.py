#!/usr/bin/env python
"""
simon.py
Simple simon game for use with pfio and the RaspberryPi interface (piface)

"""

from time import sleep 
import random
import pfio

pfio.init()	# initialise pfio (sets up the spi transfers)

first_in_squence = next()	# create the first colour in the sequence

array = [first]	# add the first colour to the array

game = 1
score = 0


while game:	#
	for i in array:
		pfio.digital_write(i,1)
		sleep(3)
		pfio.digital_write(i,0)
		sleep(1)

	for i in array:
		while (event = pfio.read_input()) == 0:
			pass

		pfio.write_output(event)
		if event != pfio.get_pin_bit_mask(i):
			game = 0
			break

		else
			sleep(1)
			pfio.digital_write(i,0)


	array.append(next())
	score +=1
	sleep(2)

pfio.write_output(0xFF)
print score

def next():
	return random.randint(1,5) 
