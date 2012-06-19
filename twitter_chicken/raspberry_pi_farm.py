#!/usr/bin/env python
"""
raspberry_pi_farm.py
contains a some singing/dancing animals on the Raspberry Pi!

author: Thomas Preston
date  : 18/06/2012
"""

import subprocess
#import pfio


VERBOSE_MODE = True


class Chicken(object):
	"""The wobbling/talking chicken"""
	def __init__(self):
		self.relay_pin = 2
		self.voice_pitch = 50 # 0-99
		self.voice_speed = 160 # words per min

	def start_wobble(self):
		"""Starts wobbling the chicken"""
		if VERBOSE_MODE:
			print "Chicken has started wobbling."
		#pfio.digitalWrite(self.relay_pin, 1)

	def stop_wobble(self):
		"""Stops wobbling the chicken"""
		if VERBOSE_MODE:
			print "Chicken has stopped wobbling."
		#pfio.digitalWrite(self.relay_pin, 0)

	def say(self, text_to_say):
		"""Makes the chicken say something"""
		if VERBOSE_MODE:
			print "Chicken says: %s" % text_to_say

		# using 'espeak' to make the chicken talk
		subprocess.call(["espeak",
			"-v", "en-rp",
			"-p", str(self.voice_pitch),
			"-s", str(self.voice_speed),
			text_to_say])
