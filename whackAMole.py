import helloworld
import time

#setup
setPinMode(1,INPUT)
setPinMode(2,INPUT)
setPinMode(3,INPUT)
setPinMode(4,INPUT)
setPinMode(5,INPUT)

setPinMode(6,OUTPUT)
setPinMode(7,OUTPUT)
setPinMode(8,OUTPUT)
setPinMode(9,OUTPUT)
setPinMode(10,OUTPUT)

current = next()
setTime = 100000
time = 0
hit = 0



while 1:
	if time ==0:
		break
	
	hit = checkHit()
	if hit:
		if hit == current:
			helloworld.writePin(current, LOW)
			current = next()
			time = setTime
			setTime -= 100
			helloworld.writePin(current,HIGH)
			hit = 0
			time.sleep(1)
		else:
			break
	time -=1

	
setAllOutput(HIGH)

	

def next()
	return random.randint(1,5) 

def checkHit()
	if checkAllInput()
		
		return hit
	else 
		return 0
