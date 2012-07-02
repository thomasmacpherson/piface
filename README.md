About
=====
This repository contains code relating to piface projects.

[PFIO Documentation](https://docs.google.com/document/d/1pSfTMevvtkBD4eyeHyry4cFMDAgvq6mMASoTBlw44TU/edit)


Installation and Setup
======================
These instructions assume you are on working on a Raspberry Pi. At
present, only the root user has the appropriate privileges to
acces the SPI module and so running programs as root is often required.
If you know how to fix this please send us an email (it'll be something
to do with when the kernel creates the /dev/spiX.Y files).

To install the piface python package you must first download the source,
move into the piface directory and then run the setup script as root:

    $ git clone https://github.com/thomasmacpherson/piface.git
    $ cd piface/
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

If you prefer, you can refer to the pfio and emulator modules directly
using the following Python syntax:

    $ sudo python
    >>> import piface.pfio as pfio
    >>> import piface.emulator as emulator
    >>> pfio.digital_write(4, 0)
    >>> emulator.digital_write(3, 1)

The emulator can be used in the same way as the pfio. Upon initialisation,
an image of the Pi Face will be drawn to a window and its inputs/outputs
can be seen.


Testing
=======
To test the installed piface package run the tests in the tests/ directory.

    $ cd tests/
    $ python piface_test.py
