"""
RacingPi Game
Contains the code for running the actual game
"""
import time
import threading
import random

import pfio


VERBOSE_MODE = True

DEFAULT_QUESTION_FILE = "racingpi/questions.txt"

class RacingPiGame(threading.Thread):
	def __init__(self, gui, question_file_name=None):
		threading.Thread.__init__(self)
		self.gui = gui

		# set up the hardware interface
		pfio.init()

		# set up the questions
		if question_file_name:
			question_file = open(question_file_name, "r")
		else:
			question_file = open(DEFAULT_QUESTION_FILE, "r")

		self.questions = list()
		for line in question_file.readlines():
			q_parts = line.split(",") # this can be moved into db later...
			self.questions.append(Question(q_parts[0], q_parts[1], q_parts[2]))

		random.shuffle(self.questions)

		# set up the buttons
		self.buttons = list()
		self.buttons.append(Button(ButtonSwitch(1), ButtonLight(3)))
		self.buttons.append(Button(ButtonSwitch(2), ButtonLight(4)))
		self.buttons.append(Button(ButtonSwitch(3), ButtonLight(5)))
		self.buttons.append(Button(ButtonSwitch(4), ButtonLight(6)))
		self.buttons.append(Button(ButtonSwitch(5), ButtonLight(7)))

		# set up the players
		self.player1 = Player("Adam", RacingCar(1), (self.buttons[0], self.buttons[1]))
		self.player2 = Player("Eve", RacingCar(2), (self.buttons[2], self.buttons[3]))

	def run(self):
		"""The main game stuff goes here"""
		while True:
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
				pin_number = pfio.get_pin_number(pin_bit_pattern)

				print "pin number: %d" % pin_number
				print self.player1.buttons[correct_answer_index].switch.pin_number

				if pin_number == self.player1.buttons[correct_answer_index].switch.pin_number:
					self.player1.buttons[correct_answer_index].light.turn_on()
					print "Player 1 got the correct answer!"
					#print "The answer was: {}".format(question.correct_answer)
					self.player1.car.drive(3)
					self.player1.buttons[correct_answer_index].light.turn_off()

				elif pin_number == self.player1.buttons[wrong_answer_index].switch.pin_number:
					self.player1.buttons[wrong_answer_index].light.turn_on()
					print "Player 1 got the WRONG answer!"
					#print "The answer was: {}".format(question.correct_answer)
					self.player2.car.drive(3)
					self.player1.buttons[wrong_answer_index].light.turn_off()

				elif pin_number == self.player2.buttons[correct_answer_index].switch.pin_number:
					self.player2.buttons[correct_answer_index].light.turn_on()
					print "Player 2 got the correct answer!"
					#print "The answer was: {}".format(question.correct_answer)
					self.player2.car.drive(3)
					self.player2.buttons[correct_answer_index].light.turn_off()

				elif pin_number == self.player2.buttons[wrong_answer_index].switch.pin_number:
					self.player2.buttons[wrong_answer_index].light.turn_on()
					print "Player 2 got the WRONG answer!"
					#print "The answer was: {}".format(question.correct_answer)
					self.player1.car.drive(3)
					self.player2.buttons[wrong_answer_index].light.turn_off()

				elif pin_number == self.buttons[4].switch.pin_number:
					self.buttons[4].light.turn_on()
					print "PASS"
					#print "The answer was: {}".format(question.correct_answer)
					time.sleep(1)
					self.buttons[4].light.turn_off()

				else:
					print "oops"
				
				# wait until nothing is pressed
				pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111
				while pin_bit_pattern != 0:
					pin_bit_pattern = pfio.read_input()[2] ^ 0b11111111

		#print "No more questions!"

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
