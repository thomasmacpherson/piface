#!/usr/bin/env python

import time
import piface.pfio

piface.pfio.init()

led1 = piface.pfio.LED(1)

while True:
  led1.turn_on()
  time.sleep(1)
  led1.turn_off()
  time.sleep(1)

# vim:ts=2:sw=2:sts=2:et:ft=python

