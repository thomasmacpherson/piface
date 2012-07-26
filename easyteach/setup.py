#!/usr/bin/env python

from distutils.core import setup

DISTUTILS_DEBUG=True

setup(name='easyteach',
	version='1.0',
	description='Tools that simplify some tasks on the Raspberry Pi in order to make teaching core programming concepts simpler.',
	author='Thomas Preston',
	author_email='thomasmarkpreston@gmail.com',
	license='GPLv3',
	packages=['easyteach'],
)
