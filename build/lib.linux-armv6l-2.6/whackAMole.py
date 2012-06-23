#!/usr/bin/env python
"""
whackAMole.py
Simple whack a mole game for use with pfio and the RaspberryPi interface (piface)

Objective of game: a random LED will light up and you must hit the corresponding button as quickly as possible.
The amount of time you have to hit the button will get shorter as the game progresses.
"""
from time import sleep
import pfio
import random


pfio.init()	# initialise pfio (sets up the spi transfers)


def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5)



current = next_colour() 	# create first random colour to be lit
pfio.digital_write(current+2,1)	# turn colour on
set_time = 10000		# time allowed to hit each light (starts off large and reduced after each hit)
time_left = set_time		# countdown timer for hitting the light
hit = 0				# the input value
score = 0


print "first pin %s " % current

while True:
	if time_left ==0:
		break	# if the light is not hit in time, exit the game while loop
	#print pfio.read_input
	in_bit_pattern = pfio.read_input()[2] ^ 0b11111111 # see if any buttons have been hit
	if in_bit_pattern:
		print "reged"
		#print "in bit pattern:      %s" % bin(in_bit_pattern)
		#print bin(current)
		#print "current bit pattern: %s" % bin(pfio.get_pin_bit_mask(current))
		if in_bit_pattern == pfio.get_pin_bit_mask(current):	# check that only the correct button was hit
			pfio.digital_write(current+2, 0)	# turn off hit light
			previous = current
			current = next_colour()		# get next colour
			while current == previous:		# ensure differnt colour each time
				current = next_colour()		# get next colour
				
			set_time -= 100			# reduce the allowed time
			time_left = set_time		# set the countdown time
			print "Time left is: %s" %time_left
			score += 1
			pfio.digital_write(current+2,1)	# turn the new light on

			sleep(1)			# leave the light on for a second
		else:
			break	# a wrong button was hit so exit the game while loop


	time_left -=1	# decrement the time left to hit the current light

	pass

pfio.write_output(0)	# turn all lights off	
print "Your score was: %s" %score
#pfio.deinit()		# close the pfio
	

