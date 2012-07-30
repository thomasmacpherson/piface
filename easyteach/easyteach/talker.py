"""
talker.py
A speech module for the Pi Face package. Provides a simple method of talking
with the Raspberry Pi.
Note: this modules doesn't actually require a Pi Face board

Essentially this is just a wrapper around espeak
"""
import subprocess


DEFAULT_PITCH = 50  # 0-99
DEFAULT_SPEED = 160 # words per min


class PiFaceTalkerError(Exception):
    pass


def say(words, pitch=None, speed=None):
    """Says words through the audio jack on the Raspberry Pi"""
    if not pitch:
        pitch = DEFAULT_PITCH

    if not speed:
        speed = DEFAULT_SPEED
 
    devnull = open("/dev/null", "w")
    try:
        subprocess.call([
            "espeak",
            "-v", "en-rp", # english received pronounciation
            "-p", str(pitch),
            "-s", str(speed),
            words],
            stderr=devnull)

    except OSError:
        raise PiFaceTalkerError(
                "There was an error running 'espeak'. Is it installed?")
