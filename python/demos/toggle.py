#!/usr/bin/env python

from time import sleep
import piface.pfio

piface.pfio.init()

# Make arrays of LEDs...
led    = [ piface.pfio.LED(i)    for i in range(1, 5) ]
# ...Switches...
switch = [ piface.pfio.Switch(i) for i in range(1, 5) ]
# ...and an array to store the switch states
down   = [ False for i in range(1, 5) ]

while True:
  for i in range(0, 4):
    if switch[i].value:
      if not down[i]:
        down[i] = True
        led[i].toggle()
    else:
      down[i] = False
  sleep(0.1)

# vim:ts=2:sw=2:sts=2:et:ft=python

