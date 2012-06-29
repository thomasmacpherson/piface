#!/usr/bin/env python

from distutils.core import setup, Extension

setup(name="spi",
	version="1.5",
	description="Python SPI access through C module for the Beagleboard XM",
	author="Brian Hensley",
	author_email="brian.e.hensley@gmail.com",
	maintainer="none",
	maintainer_email="none",
	license="GPLv2",
	url="http://www.brianhensley.net",
	ext_modules=[Extension("spi", ["spimodule.c"])])

