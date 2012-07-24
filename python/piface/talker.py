"""
talker.py
A speech module for the Pi Face package. Provides a simple method of talking
with the Raspberry Pi.
Note: this modules doesn't actually require a Pi Face board

Essentially this is just a wrapper around espeak
"""
import subprocess


pitch = 50  # 0-99
speed = 160 # words per min


class PiFaceTalkerError(Exception):
    pass


def say(words):
    """Says words through the audio jack on the Raspberry Pi"""
    global pitch
    global speed
    try:
        subprocess.call([
            "espeak",
            "-v", "en-rp", # english received pronounciation
            "-p", str(pitch),
            "-s", str(speed),
            words])

    except OSError:
        raise PiFaceTalkerError(
                "There was an error running 'espeak'. Is it installed?")
