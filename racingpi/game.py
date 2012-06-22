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

		# set up the players
		self.player1 = Player("Adam", RacingCar(1), (self.buttons[0], self.buttons[1]))
		self.player2 = Player("Eve", RacingCar(2), (self.buttons[2], self.buttons[3]))

	def run(self):
		"""The main game stuff goes here"""
		for question in self.questions:
			# ask a question
			correct_answer_index = int(2 * random.random())
			wrong_answer_index = correct_answer_index ^ 1
			answers = ["", ""]
			answers[correct_answer_index] = question.correct_answer
			answers[wrong_answer_index] = question.wrong_answer

			values = [question.text]
			values.extend(answers)
			self.gui.update_question("%s\nA: %s\nB: %s" % tuple(values))

			# wait for a button press
			pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111
			while pin_bit_pattern == 0:
				pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111

			# find out which button was pressed
			if self.player1.buttons[correct_answer_index].switch.value == 1:
				print "Player 1 got the correct answer!"
				self.player1.car.drive(3)

			elif self.player1.buttons[wrong_answer_index].switch.value == 1:
				print "Player 1 got the WRONG answer!"
				self.player2.car.drive(3)

			elif self.player2.buttons[correct_answer_index].switch.value == 1:
				print "Player 2 got the correct answer!"
				self.player2.car.drive(3)

			elif self.player2.buttons[wrong_answer_index].switch.value == 1:
				print "Player 2 got the WRONG answer!"
				self.player1.car.drive(3)

			elif self.buttons[4].switch.value == 1:
				print "PASS"
				pass
				

			# wait until nothing is pressed
			pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111
			while pin_bit_pattern != 0:
				pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111

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
	def __init__(self, name, car, buttons):
		self.name = name
		self.car = car
		self.buttons = buttons
		self.points = 0

class Question(object):
	def __init__(self, question_text, correct_answer, wrong_answer):
		self.text = question_text
		self.correct_answer = correct_answer
		self.wrong_answer = wrong_answer
