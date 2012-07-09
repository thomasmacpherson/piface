#!/usr/bin/env python
"""
twitter_listen.py
listens for new tweets containing a search term and then wobbles a chicken

author: Thomas Preston
date  : 18/06/2012
"""

import time
import sys
import twitter

import raspberry_pi_farm


DEFAULT_SEARCH_TERM = "chicken"
TIME_DELAY = 2 # seconds between each status check

def main():
	api = twitter.Api()
	previous_status = twitter.Status()
	raspberry_pi_farm.init()
	chicken = raspberry_pi_farm.Chicken()

	# what are we searching for?
	if len(sys.argv) > 1:
		search_term = sys.argv[1]
	else:
		search_term = DEFAULT_SEARCH_TERM

	print "Listening to tweets containing the word '%s'." % search_term

	while True:
		# grab the first tweet containing the search_term
		current_status = api.GetSearch(term=search_term, per_page=1)[0]

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
