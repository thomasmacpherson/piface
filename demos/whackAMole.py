#!/usr/bin/env python
"""
whackAMole.py
Simple whack a mole game for use with pfio and the RaspberryPi interface (piface)

Objective of game: A random LED will light up and you must hit the corresponding button as quickly as possible.
The amount of time you have to hit the button will get shorter as the game progresses.
"""

from time import sleep		# for delays
import random			# for generating the next random button flash

import piface.pfio as pfio			# piface library		


pfio.init()			# initialise pfio (sets up the spi transfers)


def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5)



current = next_colour() 			# create first random colour to be lit
pfio.digital_write(current+2,1)			# turn colour on
set_time = 2000					# time allowed to hit each light (starts off large and reduced after each hit)
time_left = set_time				# countdown timer for hitting the light
hit = 0						# the input value
score = 0					# keep track of the player's score
misses = 0					# keep track of how many the player misses

colours = ["Red","Green","Blue","Yellow","White"]	# colour list for printing to screen
previous_pressed = 255


print "Time left is: %s" %time_left		# notify the player how long they have to hit each flash


while True:

	in_bit_pattern = pfio.read_input()[2] ^ 0b11111111 # see if any buttons have been hit
	
	if in_bit_pattern != previous_pressed:		# check this is a new button press
		previous_pressed = in_bit_pattern	# record button press for next time's check

		if in_bit_pattern > 0:

			if in_bit_pattern == pfio.get_pin_bit_mask(current):	# check that only the correct button was hit
			
				pfio.digital_write(current+2, 0)		# turn off hit light
				previous = current
				current = next_colour()				# get next colour
			
				while current == previous:			# ensure differnt colour each time
					current = next_colour()			# get next colour
				
				if ((score + misses) %30) ==29:
					if set_time > 100:
						set_time /= 2			# reduce the time allowed to hit the light
						print "Time left is: %s" %set_time
			
				time_left = set_time				# set the countdown time
			
				score += 1
				print "Your score %d" %score
				pfio.digital_write(current+2,1)			# turn the new light on
			

			else:							# wrong button pressed
				print "Wrong one!"
				print "Your score %d" %score
				score -= 1
			
			
	elif time_left==0:
		pfio.digital_write(current+2, 0)			# turn off hit light
		misses +=1						# increment misses
		print "Missed one!"
		
		if misses == 10:					# too many misses = Game Over!
			break
			
		previous = current					#
		current = next_colour()					# get next colour
		
		while current == previous:				# ensure differnt colour each time
			current = next_colour()				# get next colour
				
		if ((score + misses) %30)==29:
			if set_time > 100:
				set_time /= 2				# reduce the allowed time
				print "Time left is: %s" %set_time
				
		time_left = set_time					# set the countdown time
			
		pfio.digital_write(current+2,1)				# turn the new light on		
	
	time_left -=1							# decrement the time left to hit the current light

	

pfio.write_output(0)				# turn all lights off	
print "\nGame over!\n"
print "Your score was: %s" %score		# print the player's final score
#pfio.deinit()					# close the pfio
	

