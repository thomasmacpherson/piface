"""
RacingPi Game
Contains the code for running the actual game
"""
import time
import threading
import random

import pfio


VERBOSE_MODE = True


class RacingPiGame(threading.Thread):
	def __init__(self, gui):
		threading.Thread.__init__(self)
		self.gui = gui

		# set up the hardware interface
		pfio.init()

		# set up the players
		self.player1 = Player("Adam", RacingCar(1))
		self.player2 = Player("Eve", RacingCar(2))

		# set up the questions
		question_file = open("racingpi/questions.txt", "r")
		self.questions = list()
		for line in question_file.readlines():
			q_parts = line.split(",") # this can be moved into db later...
			self.questions.append(Question(q_parts[0], q_parts[1], q_parts[2]))

		random.shuffle(self.questions)

		# set up the buttons
		self.buttons = list()
		self.buttons.append(Button(ButtonSwitch(1), ButtonLight(1)))
		self.buttons.append(Button(ButtonSwitch(2), ButtonLight(2)))
		self.buttons.append(Button(ButtonSwitch(3), ButtonLight(3)))
		self.buttons.append(Button(ButtonSwitch(4), ButtonLight(4)))
		self.buttons.append(Button(ButtonSwitch(5), ButtonLight(5)))

	def run(self):
		"""The main game stuff goes here"""
		for question in self.questions:
			# ask a question
			self.gui.update_question(question.text) # TODO: something with answers

			# wait for a button press
			pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111
			while pin_bit_pattern == 0:
				pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111

			#pin_number = pfio.get_pin_number(pin_bit_pattern)
			for button in self.buttons:
				print button.switch.value

			# wait until nothing is pressed
			pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111
			while pin_bit_pattern != 0:
				pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111

			# check answer

class RacingCar(pfio.Relay):
	def __init__(self, racing_car_number):
		# racing car number directly translates to the relay number
		pfio.Relay.__init__(self, racing_car_number)
	
	def drive(self, drive_period):
		" ""Move the car for the specified amount of seconds"" "
		self.turn_on()
		time.sleep(drive_period)
		self.turn_off()

class ButtonLight(pfio.Item):
	def __init__(self, button_number):
		# button lights are connected directly to pins
		pfio.Item.__init__(self, button_number)

class ButtonSwitch(pfio.Item):
	def __init__(self, button_number):
		# button switches are connected directly to pins
		pfio.Item.__init__(self, button_number, True) # input

class Button(object):
	def __init__(self, button_switch, button_light):
		self.switch = button_switch
		self.light = button_light

class Player(object):
	def __init__(self, name, car):
		self.name = name
		self.car = car
		self.points = 0

class Question(object):
	def __init__(self, question_text, right_answer, wrong_answer):
		self.text = question_text
		self.right_answer = right_answer
		self.wrong_answer = wrong_answer
