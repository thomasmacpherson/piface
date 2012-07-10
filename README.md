About
=====
This repository contains code relating to piface projects.

[PiFace Downloads](http://pi.cs.man.ac.uk/download)

[Setting up the Raspberry Pi for use with PiFace](https://docs.google.com/document/d/145TkSMwnPAJaqKMLxdvD8aGULQ8UgIIU3hg-JAKwAa0/edit)

[Python PFIO Documentation](https://docs.google.com/document/d/1pSfTMevvtkBD4eyeHyry4cFMDAgvq6mMASoTBlw44TU/edit)

[C PFIO Documentation](https://docs.google.com/document/d/1M-Rb1Ox-C8oBIhDCE_e0yn1KvbEykMnJZ4aUwCc8Aec/edit)

Installation and Setup
======================
These instructions assume you are on working on a Raspberry Pi with a 
kernel that supports the SPI devices (we're using [bootc](http://www.bootc.net/)).
and that the user 'pi' has read/write access to /dev/spidev*. This can
be set up using the spidev_setup.sh script in scripts/.

A more comprehensive walkthrough can be found in the links at the top of
this README file.

### Python
To install the piface python package you must first download the source,
move into the piface directory and then run the setup script as root:

    $ git clone https://github.com/thomasmacpherson/piface.git
    $ cd piface/python/
    $ sudo python setup.py install

Now whenever you enter a python shell you can access the piface's
input/output module or the emulator by importing them as such:

    $ python
    >>> import piface.pfio
    >>> piface.pfio.digital_write(1, 1)
    >>> led1 = piface.pfio.LED(1)
    >>> led1.turn_off()
    >>> import piface.emulator
    >>> piface.emulator.init()

If you prefer, you can refer to the pfio and emulator modules directly
using the following Python syntax:

    $ python
    >>> import piface.pfio as pfio
    >>> import piface.emulator as emulator
    >>> pfio.digital_write(4, 0)
    >>> emulator.digital_write(3, 1)

The emulator can be used in the same way as the pfio. Upon initialisation,
an image of the Pi Face will be drawn to a window and its inputs/outputs
can be seen.

### C
To install the C pfio library download the source, move into the C directory,
call the setup scripts and then (as root) run the install command:

    $ git clone https://github.com/thomasmacpherson/piface.git
    $ cd piface/c/
    $ ./autogen.sh && ./configure && make
    $ su
    # make install

Testing
=======
### Python
To test the installed piface package run the tests in the tests/ directory.

    $ cd python/tests/
    $ python piface_test.py
