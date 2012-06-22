"""
RacingPi Game
Contains the code for running the actual game
"""
import time
import threading

import pfio

class RacingPiGame(threading.Thread):
	def __init__(self, gui):
		threading.Thread.__init__(self)
		self.gui = gui

	def run(self):
		"""The main game stuff goes here"""
		time.sleep(3)
		self.gui.update_question("What do you mean? An African or European swallow?")

		player1 = Player("Adam", RacingCar(1))
		player2 = Player("Eve", RacingCar(2))

		player1.points += 3
		player1.car.drive(3)


class RacingCar(pfio.Relay):
	def __init__(self, racing_car_number):
		# racing car number directly translates to the relay number
		pfio.Relay.__init__(self, racing_car_number)
	
	def drive(self, drive_period):
		"""Move the car for the specified amount of seconds"""
		self.turn_on()
		time.sleep(drive_period)
		self.turn_off()

class Player(object):
	def __init__(self, name, car):
		self.name = name
		self.car = car
		self.points = 0
