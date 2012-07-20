from time import sleep

#import piface.emulator as pfio
import piface.pfio as pfio


if __name__ == "__main__":
    pfio.init()
    while True:
        pfio.write_output(0xff)
        sleep(1)
        pfio.write_output(0)
        sleep(1)
