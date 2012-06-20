from time import sleep
import random



import PFIO
PFIO.init()

first = next()

array = [first]

game = 1


while game:
	for i in array:
		PFIO.digital_write(i,1)
		sleep(3)
		PFIO.digital_write(i,0)
		sleep(1)

	for i in array:
		while (event = PFIO.read_input()) == 0:
			pass
		PFIO.digital_write(i,1)

		if event != i:
			game = 0
			break

		else
			sleep(1)
			PFIO.digital_write(i,0)


	array.append(next())
	sleep(2)



def next():
	return random.randint(1,5) 
