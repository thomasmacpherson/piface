#!/usr/bin/env python
"""
raspberry_pi_farm.py
contains a some singing/dancing animals on the Raspberry Pi!

author: Thomas Preston
date  : 18/06/2012
"""

import subprocess
import piface.pfio as pfio
#import piface.emulator as pfio
import easyteach.talker as talker


VERBOSE_MODE = True


class Chicken(pfio.Relay):
    """The wobbling/talking chicken"""
    def __init__(self):
        pfio.Relay.__init__(self, 1) # chicken is on pin 
        self.relay_pin = 1
        self.voice_pitch = 50 # 0-99
        self.voice_speed = 160 # words per min

    def start_wobble(self):
        """Starts wobbling the chicken"""
        self.turn_on()
        if VERBOSE_MODE:
            print "Chicken has started wobbling."

    def stop_wobble(self):
        """Stops wobbling the chicken"""
        self.turn_off()
        if VERBOSE_MODE:
            print "Chicken has stopped wobbling."

    def say(self, text_to_say):
        """Makes the chicken say something"""
        if VERBOSE_MODE:
            print "Chicken says: %s" % text_to_say

        talker.say(text_to_say, self.voice_pitch, self.voice_speed)


def init():
    """Initialises the raspberry pi farm"""
    pfio.init()
