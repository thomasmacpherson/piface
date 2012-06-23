#!/usr/bin/env python
"""
simon.py
Simple simon game for use with pfio and the RaspberryPi interface (piface)

"""

from time import sleep 
import random
import pfio

pfio.init()	# initialise pfio (sets up the spi transfers)

colours = ["Red","Green","Blue","Yellow","White"]
sounds = [0.001,0.002,0.003,0.004,0.005]

def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5) 

first_in_sequence = next_colour()	# create the first colour in the sequence

array = [first_in_sequence]	# add the first colour to the array

game = 1	# keep track of game active (1 for active, 0 for game over)
score = 0	

sleep(1) # let them get their bearings
while game:	# while game in play
	game_round = score+1
	print "\nRound %s!" %game_round
	for i in array:		# for each colour in current sequence (flash the sequence)

		pfio.digital_write(i+2,1)	# turn the colour on
		pfio.digital_write(1+i%2,1)
		sleep(sounds[i-1])
		pfio.digital_write(1+i%2,0)
		
		print colours[i-1]
		sleep(0.5)		# wait to keep the colour showing 
		pfio.digital_write(i+2,0)	# turn the colour off
		sleep(0.2)	# small break between colours
		

	sleep(0.4)
	pfio.write_output(0xFF)		# signify their turn
	sleep(0.3)
	pfio.write_output(0x0)	
	print "\nYour turn!"

	for i in array:	# for each colour in current sequence (check against inputted sequence)
		event = pfio.read_input()[2] ^ 0b11111111	# read the button port state
		
		while event != 0:					# wait till no buttons pressed
			event = pfio.read_input()[2] ^ 0b11111111	# so a single button press is not read as 2
			
			
					
		while event == 0:					# wait for any input 
			event = pfio.read_input()[2] ^ 0b11111111
			
		pin_number = pfio.get_pin_number(event)			# calculate the input pin
		
		print colours[pin_number -1]		# print the colour in sequence to the screen
		
		pfio.digital_write(pin_number+2,1)	# light up the buttons pressed
		if event != pfio.get_pin_bit_mask(i):	
			game = 0			# if any wrong buttons were pressed end the game
			break

		else:					# otherwise turn the button led off and leave a small break
			previous = event
			event = pfio.read_input()[2] ^ 0b11111111
			while previous == event:
				previous = event
				event = pfio.read_input()[2] ^ 0b11111111
			pfio.digital_write(i+2,0)
			
			
	sleep(0.4)
	pfio.write_output(0xFF)		# signify their turn
	sleep(0.3)
	pfio.write_output(0x0)	

	next = next_colour()
	while next == array[-1]:
		next = next_colour()
	array.append(next)	# add another colour to the sequence
	score +=1	# increment the score counter
	sleep(0.4)	# small break before flashing the new extended sequence

pfio.write_output(0x00)		# if the game has been lost, set all the button leds on
#pfio.deinit()			# close the pfio

print "Your score was: %s" %score 	# print the players score
