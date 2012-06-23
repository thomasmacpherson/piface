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
set_time = 2000		# time allowed to hit each light (starts off large and reduced after each hit)
time_left = set_time		# countdown timer for hitting the light
hit = 0				# the input value
score = 0
misses = 0

colours = ["Red","Green","Blue","Yellow","White"]



print "Time left is: %s" %time_left

while True:
	#print pfio.read_input
	in_bit_pattern = pfio.read_input()[2] ^ 0b11111111 # see if any buttons have been hit
	#TODO: insert check for button release (while 0)
	if in_bit_pattern > 0:
		print "in bit pattern:      %s" % bin(in_bit_pattern)
		print bin(current)
		print "current bit pattern: %s" % bin(pfio.get_pin_bit_mask(current))
		if in_bit_pattern == pfio.get_pin_bit_mask(current):	# check that only the correct button was hit
			pfio.digital_write(current+2, 0)	# turn off hit light
			previous = current
			current = next_colour()		# get next colour
			while current == previous:		# ensure differnt colour each time
				current = next_colour()		# get next colour
				
			if ((score + misses) %50) ==49:
					set_time /= 2			# reduce the allowed time
					print "Time left is: %s" %time_left
			time_left = set_time		# set the countdown time
			
			score += 1
			pfio.digital_write(current+2,1)	# turn the new light on

			#sleep(1)			# leave the light on for a second

		else:
			print "shit"
			score -= 1
	elif time_left==0:
			pfio.digital_write(current+2, 0)	# turn off hit light
			misses +=1
			if misses == 10:
				break
			previous = current
			current = next_colour()			# get next colour
			while current == previous:		# ensure differnt colour each time
				current = next_colour()		# get next colour
				
			if ((score + misses) %50)==49:
					set_time /= 2		# reduce the allowed time
					print "Time left is: %s" %time_left
			time_left = set_time		# set the countdown time
			
			score += 1
			pfio.digital_write(current+2,1)	# turn the new light on		
	
	time_left -=1	# decrement the time left to hit the current light

	

pfio.write_output(0)	# turn all lights off	
print "Your score was: %s" %score
#pfio.deinit()		# close the pfio
	

