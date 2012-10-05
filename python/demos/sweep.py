#!/usr/bin/env python

import time
import piface.pfio
import piface.emulator

# Set thing to 
#   piface.emulator    to run with emulator
#   piface.pfio        to run without emulator

#thing = piface.emulator
thing = piface.pfio

thing.init()

led1 = thing.LED(1)

while True:
  for i in range(1, 5):
    led = thing.LED(i)
    led.turn_on()
    time.sleep(0.5)
    led.turn_off()

# vim:ts=2:sw=2:sts=2:et:ft=python

