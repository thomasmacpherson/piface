#!/usr/bin/env python
"""
simon.py
Simple simon game for use with pfio and the RaspberryPi interface (piface)

"""

from time import sleep 
import random
import pfio

pfio.init()	# initialise pfio (sets up the spi transfers)

first_in_squence = next_colour()	# create the first colour in the sequence

array = [first]	# add the first colour to the array

game = 1	# keep track of game active (1 for active, 0 for game over)
score = 0	


while game:	# while game in play
	for i in array:	# for each colour in current sequence (flash the sequence)

		pfio.digital_write(i,1)	# turn the colour on
		sleep(2)		# wait to keep the colour showing 
		pfio.digital_write(i,0)	# turn the colour off
		sleep(1)	# small break between colours

	for i in array:	# for each colour in current sequence (check against inputted sequence)

		while (event = pfio.read_input()) == 0:	# wait for any input 
			pass

		pfio.write_output(event)		# light up the buttons pressed
		if event != pfio.get_pin_bit_mask(i):	
			game = 0			# if any wrong buttons were pressed end the game
			break

		else					# otherwise turn the button led off and leave a small break
			pfio.digital_write(i,0)
			sleep(1)
			


	array.append(next_colour())	# add another colour to the sequence
	score +=1	# increment the score counter
	sleep(2)	# small break before flashing the new extended sequence

pfio.write_output(0xFF)		# if the game has been lost, set all the button leds on
print "Your score was: {}".format(score) 	# print the players score

def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5) 
