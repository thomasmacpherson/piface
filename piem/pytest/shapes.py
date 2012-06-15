#! /usr/bin/env python
import framework
from math import pi

class Shapes(framework.Screen):
    def draw(self, cr, width, height):
        cr.set_source_rgb(0.5, 0.5, 0.5)
        cr.rectangle(0, 0, width, height)
        cr.fill()

        # draw a rectangle
        cr.set_source_rgb(1.0, 1.0, 1.0)
        cr.rectangle(10, 10, width - 20, height - 20)
        cr.fill()

        # draw lines
        cr.set_source_rgb(0.0, 0.0, 0.8)
        cr.move_to(width / 3.0, height / 3.0)
        cr.rel_line_to(0, height / 6.0)
        cr.move_to(2 * width / 3.0, height / 3.0)
        cr.rel_line_to(0, height / 6.0)
        cr.stroke()

        # and a circle
        cr.set_source_rgb(1.0, 0.0, 0.0)
        radius = min(width, height)
        cr.arc(width / 2.0, height / 2.0, radius / 2.0 - 20, 0, 2 * pi)
        cr.stroke()
        cr.arc(width / 2.0, height / 2.0, radius / 3.0 - 10, pi / 3, 2 * pi / 3)
        cr.stroke()

framework.run(Shapes)
