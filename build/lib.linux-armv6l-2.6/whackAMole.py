#!/usr/bin/env python
"""
whackAMole.py
Simple whack a mole game for use with pfio and the RaspberryPi interface (piface)

Objective of game: a random LED will light up and you must hit the corresponding button as quickly as possible.
The amount of time you have to hit the button will get shorter as the game progresses.
"""

from time import sleep
import PFIO


PFIO.init()	# initialise pfio (sets up the spi transfers)

current = next_colour() 	# create first random colour to be lit
PFIO.digital_write(current,1)	# turn colour on
set_time = 100000		# time allowed to hit each light (starts off large and reduced after each hit)
time_left = set_time		# countdown timer for hitting the light
hit = 0				# the input value



while True:
	if time_left ==0:
		break	# if the light is not hit in time, exit the game while loop
	
	hit = pfio.read_input() # see if any buttons have been hit
	if hit:
		if hit == pfio.get_bit_mask(current):	# check that only the correct button was hit
			pfio.digital_write(current, 0)	# turn off hit light
			current = next_colour()		# get next colour
			set_time -= 100			# reduce the allowed time
			time_left = setTime		# set the countdown time
			pfio.digital_write(current,1)	# turn the new light on

			sleep(1)			# leave the light on for a second
		else:
			break	# a wrong button was hit so exit the game while loop


	time_left -=1	# decrement the time left to hit the current light


pfio.write_output(0)	# turn all lights off	

pfio.deinit()		# close the pfio
	

def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5)
