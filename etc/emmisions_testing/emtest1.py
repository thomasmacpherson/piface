from time import sleep

import piface.emulator as pfio
#import piface.pfio as pfio


if __name__ == "__main__":
    pfio.init()
    while True:
        # turn each output off, one by one
        for i in range(1, 9):
            pfio.digital_write(i, 1)
            sleep(1)
            pfio.digital_write(i, 0)
            sleep(1)
