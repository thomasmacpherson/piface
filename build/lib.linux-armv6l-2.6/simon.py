from time import sleep
import random



import PFIO
PFIO.init()

first = next()

array = [first]


while True:
	for i in array:
		PFIO.digitalWrite(i,1)
		sleep(3)
		PFIO.digitalWrite(i,0)
		sleep(1)

	PFIO.dig





def next():
	return random.randint(1,5) 
