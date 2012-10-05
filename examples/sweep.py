#!/usr/bin/env python

import time
import piface.pfio

piface.pfio.init()

led1 = piface.pfio.LED(1)

while True:
  for i in range(1, 5):
    led = piface.pfio.LED(i)
    led.turn_on()
    time.sleep(0.5)
    led.turn_off()

# vim:ts=2:sw=2:sts=2:et:ft=python

