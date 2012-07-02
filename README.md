About
=====
This repository contains code relating to piface projects.

For access to documentation use google docs

Installation and Setup
======================
These instructions assume you are on working on a Raspberry Pi. At
present, only the root user has the appropriate privileges to
acces the SPI module and so running programs as root is often required.
If you know how to fix this please send us an email (it'll be something
to do with when the kernel creates the /dev/spiX.Y files).

To get the source and demo programs type:
    $ git clone https://github.com/thomasmacpherson/piface.git

Then to install, move into the piface directory and type:
    $ sudo python setup.py install

Now whenever you enter a python shell you can access the piface's
input/output module or the emulator by importing them as such:
    $ sudo python
    >>> import piface.pfio
    >>> piface.pfio.digital_write(1, 1)
    >>> led1 = piface.pfio.LED(1)
    >>> led1.turn_off()
    >>> import piface.emulator
    >>> piface.emulator.init()
