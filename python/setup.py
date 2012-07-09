#!/usr/bin/env python

from distutils.core import setup, Extension

DISTUTILS_DEBUG=True

setup(name='piface',
	version='1.0',
	description='Tools for interacting with the Pi Face add-on to the Raspberry Pi',
	author='Thomas Macpherson-Pope, Thomas Preston',
	author_email='thomas.macpherson-pope@student.manchester.ac.uk, thomasmarkpreston@gmail.com',
	license='GPLv3',
	url='http://pi.cs.man.ac.uk/interface.htm',
	packages=['piface'],
	ext_modules=[Extension('piface/spi', ['piface/spimodule.c'])],
	package_data={'piface' : ['images/*.png']},
)
