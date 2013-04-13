News
====
15/02/2013 - We're making the project more modular and so future development
on the indvidual components will take place in component specific repositories.
This repo will remain maintained but no new major features will be added.

If you would like to use the most up-to-date software, use the following links:

[piface](https://github.com/piface/)

About
=====
This repository contains code relating to piface projects.

*The software in this repository uses Python 2 and is incompatible with Python 3*

[Farnell Documentation](http://www.farnell.com/datasheets/1684425.pdf)

[Getting Started](https://docs.google.com/document/d/145TkSMwnPAJaqKMLxdvD8aGULQ8UgIIU3hg-JAKwAa0/edit)

[Documentation](https://docs.google.com/folder/d/0B-UAZ9CyJCLGQjJ3RDlqa2pqaDg/edit)

[Downloads](http://pi.cs.man.ac.uk/download)

Installation and Setup
======================
Please refer to the [Farnell Documentation](http://www.farnell.com/datasheets/1684425.pdf)
for simple instructions.

If you'd like to do things by yourself then the following might be of some use.

\# is the root user prompt, $ is the normal user (pi) prompt. You can prefix user
commands with *sudo* to run them with root user privileges.

### Enabling the SPI module
PiFace Digital communicates with the Raspberry Pi using the SPI interface.
The SPI interface driver is included in the later Raspbian distributions
but is not enabled by default.

To load the SPI driver manually, type:

    # modprobe spi-bcm2708

*This will not persist after a reboot.* To permanently enable the SPI module
comment out the spi module blacklist line in /etc/modprobe.d/raspi-blacklist.conf
(you will have to be root).

### Dependencies
Everything (if you're unsure, just run this one)

    # apt-get install python-dev python-gtk2-dev git automake libtool espeak python-django python-simplejson

Just Python

    # apt-get install python-dev python-gtk2-dev git

Just C

    # apt-get install automake libtool

Easyteach:

    # apt-get install espeak

Web Interface

    # apt-get install python-django python-simplejson
    
### Getting the source
To download all of the source files simply run the following command:

    $ git clone https://github.com/thomasmacpherson/piface.git

This will create a directory called *piface*, which contains the entire
project tree stored in this Git repository.

### Python
To install the piface python package you must first download the source,
move into the piface directory and then run the setup script as root (ignore
the compiler warnings about data types not matching up, it's just being
picky!):

    $ cd piface/python/
    $ sudo python setup.py install

Now whenever you enter a python shell you can access the piface's
input/output module or the emulator by importing them like so:

    $ python
    >>> import piface.pfio
    >>> piface.pfio.init()
    >>> piface.pfio.digital_write(1, 1)
    >>> led1 = piface.pfio.LED(1)
    >>> led1.turn_off()
    >>> import piface.emulator
    >>> piface.emulator.init()

*Note: Make sure you have left the python source directory before importing
any modules, otherwise Python may get confused*

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

You can find some example python scripts in python/demos.

If you would like to remove the PiFace Python libraries, issue the following command:

     $ sudo rm -r /usr/local/lib/python2.7/dist-packages/{piface,piface-1.0.egg-info}

### C
To install the C pfio library download the source, move into the C directory,
call the setup scripts and then (as root) run the install command:

    $ cd piface/c/
    $ ./autogen.sh && ./configure && make && sudo make install
    
To use the C libraries you will need to include the pfio header file from 
the piface library and then compile with the correct flags:

    $ cat piface_program.c
    #include <libpiface-1.0/pfio.h>

    int main(void)
    {
       pfio_init();
       pfio_digital_write(1, 1);
       pfio_deinit();
    }
    $ gcc -L/usr/local/lib/ -lpiface-1.0 -o piface_program piface_program.c
    $ ./piface_program

Testing
=======
### Python
To test the installed piface package run the tests in the tests/ directory.

    $ cd python/tests/
    $ python piface_test.py
