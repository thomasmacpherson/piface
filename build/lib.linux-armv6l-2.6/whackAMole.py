from time import sleep


import PFIO


PFIO.init()

current = next()
PFIO.digitalWrite(current,0)
setTime = 100000
time = 0
hit = 0



while True:
	if time ==0:
		break
	
	hit = checkHit()
	if hit:
		if hit == current:
			PFIO.digitalWrite(current, 0)
			current = next()
			time = setTime
			setTime -= 100
			PFIO.digitalWrite(current,1)
			hit = 0
			time.sleep(1)
		else:
			break
	time -=1

	

PFIO.deinit()
	

def next():
	return random.randint(1,5) 

def checkHit():
	check = 0
	check = check | digitalRead(1) |digitalRead(2) | digitalRead(3) | digitalRead(4) | digitalRead(5)
	

	return check

