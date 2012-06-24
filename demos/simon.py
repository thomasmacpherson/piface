#!/usr/bin/env python
"""
simon.py
Simple simon game for use with pfio and the RaspberryPi interface (piface)

Objective of the game: You must remember an ever increasing sequence of flashes and input them correctly*

"""

from time import sleep 		# for delays
import random			# for random sequence generation
import pfio			# piface library




pfio.init()			# initialise pfio (sets up the spi transfers)

colours = ["Red","Green","Blue","Yellow","White"]		# colour names for printing to screen



def next_colour():
	""" choses a random number between 1 and 5 to represent the coloured leds and their corresponding buttons"""
	return random.randint(1,5) 



first_in_sequence = next_colour()	# create the first colour in the sequence

array = [first_in_sequence]		# add the first colour to the array

game = 1				# keep track of game active (1 for active, 0 for game over)
score = 0				# keep track of player's score
screen_output = False			# choice to write colours and cues to the screen


sleep(1) # let them get their bearings

while game:						# while game in play
	
	game_round = score+1				
	
	if screen_output:				# print the round number
		print "\nRound %s!" %game_round
		
	for i in array:					# for each colour in current sequence (flash the sequence)

		pfio.digital_write(i+2,1)		# turn the colour on

		
		if screen_output:			# print the colour to the screen
			print colours[i-1]
			
		sleep(0.5)				# wait to keep the colour showing 
		pfio.digital_write(i+2,0)		# turn the colour off
		sleep(0.2)				# small break between colours
		

	sleep(0.4)
	pfio.write_output(0xFF)				# signify it is their turn by turning all the LEDs on then off
	sleep(0.3)
	pfio.write_output(0x0)
	
	if screen_output:	
		print "\nYour turn!"


	for i in array:						# for each colour in current sequence (check against inputted sequence)
		event = pfio.read_input()[2] ^ 0b11111111		# read the button port state
		
		while event != 0:					# wait till no buttons pressed
			event = pfio.read_input()[2] ^ 0b11111111	# so a single button press is not read as 2
			
				
		while event == 0:					# wait for any input 
			event = pfio.read_input()[2] ^ 0b11111111
			
		pin_number = pfio.get_pin_number(event)			# calculate the input pin
		
		if screen_output:
			print colours[pin_number -1]			# print the colour in sequence to the screen
		
		pfio.digital_write(pin_number+2,1)			# light up the buttons pressed
		
		if event != pfio.get_pin_bit_mask(i):	
			game = 0					# if any wrong buttons were pressed end the game
			break

		else:							# otherwise the correct button was pressed
			previous = event
			event = pfio.read_input()[2] ^ 0b11111111
			
			while previous == event:				# while the button is held down, wait
				previous = event
				event = pfio.read_input()[2] ^ 0b11111111
				
			pfio.digital_write(i+2,0)				# turn the button's LED off
			
			
	sleep(0.4)
	pfio.write_output(0xFF)		# signify their turn is over
	sleep(0.3)
	pfio.write_output(0x0)	

	if game:
		next = next_colour()		# set next colour
		while next == array[-1]:	# ensure the same colour isn't chosen twice in a row
			next = next_colour()
		
		array.append(next)		# add another colour to the sequence
		score +=1			# increment the score counter
		sleep(0.4)			# small break before flashing the new extended sequence



pfio.write_output(0x00)			# if the game has been lost, set all the button leds off

print "Your score was %s" %score 	# print the players score

"""
f = open('high_scores.txt','r+')

high_scores = f.readlines()


high_score = 0
index = 0

for indx, line in enumerate(high_scores):
	if "simon" in line:
		line = line.split(",")
		high_score = int(line[1])
		index = indx
		break 
		
f.close()

print "The high score was %d" %high_score


if score > high_score:
	print "Congratulations! You have the new high score"
	f = open('high_scores.txt','r+')
	f.write(replace(str(high_score),str(score)))
	f.close()
else:
	print "You haven't beaten the high score, keep trying!"

"""
pfio.deinit()				# close the pfio
