"""
"""
import time
import threading

class RacingPiGame(threading.Thread):
	def __init__(self, gui):
		threading.Thread.__init__(self)
		self.gui = gui

	def run(self):
		"""The main game stuff goes here"""
		time.sleep(3)
		self.gui.update_question("What do you mean? An African or European swallow?")
