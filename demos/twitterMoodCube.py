#!/usr/bin/env python
"""
twitterMoodCube.py

Simple moode cube that reflects the mood of the world and allows you to send your mood via a status post
author: Thomas Macpherson-Pope
date  : 20/06/2012
"""

from time import sleep
import twitter
import piface.pfio as pfio


pfio.init()

twitter = twitter.Api()

terms = ["#happy","#sad","#angry","#jelous","#guilty"]

search_term = terms[0]

twitter.GetSearch(term=search_term)
