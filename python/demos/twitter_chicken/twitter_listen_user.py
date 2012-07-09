#!/usr/bin/env python
"""
twitter_listen_user.py
listens for new tweets and then wobbles a chicken

author: Thomas Preston
date  : 18/06/2012
"""

import time
import sys
import twitter

import raspberry_pi_farm


DEFAULT_USER = "tommarkpreston" # the default user we should follow
TIME_DELAY = 2 # seconds between each status check

def main():
	api = twitter.Api()
	previous_status = twitter.Status()
	raspberry_pi_farm.init()
	chicken = raspberry_pi_farm.Chicken()

	# who are we listening to?
	if len(sys.argv) > 1:
		user = sys.argv[1]
	else:
		user = DEFAULT_USER

	print "Listening to tweets from '%s'." % user

	while True:
		# grab the users current status
		current_status = api.GetUser(user).status

		# if the status is different then give it to the chicken
		if current_status.id != previous_status.id:
			chicken.start_wobble()
			chicken.say(current_status.text)
			chicken.stop_wobble()

			previous_status = current_status

		# wait for a short while before checking again
		time.sleep(TIME_DELAY)
	
if __name__ == "__main__":
	main()
