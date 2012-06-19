
#Python example for SPI bus, written by Brian Hensley
#This script will take any amount of Hex values and determine
#the length and then transfer the data as a string to the "spi" module
import spi
from time import sleep

#At the beginning of the program open up the SPI port.
#this is port /dev/spidevX.Y
#Being called as as spi.SPI(X,Y)



def send(data):
	#Calculates the length, and devides by 2 for two bytes of data sent.
	length_data = len(data[0])/2

	#transfers data string
	#print 'Value transfered to C spimodule:',data
	h = a.transfer(data[0], length_data)
	print "trans"
	print h
	#hhex = [hex(x) for x in h]

	#string = ""
	#for i in hhex:
	#	string = string + i.replace("0x", "")

	return h



def pinTranslation(pin):
	return 2**(pin-1)



def digitalWrite(pinNumber, value):
	print "digital Write start"

	pinNumber = pinTranslation(pinNumber)
	print pinNumber

	temp = readOutput()
	print temp
	#temp = temp[2:4]
	#current = int(temp,16)
	current = temp[2]
	print "new"
	print current
	
	print "before"
	#print bin(current)[2:]

	if value:
		current = current | pinNumber
	else:
		current = current & ~pinNumber
	print current
	print bin(current)[2:]
	current = hex(current)
	print "after"
	print current
	something = "4012"

	if int(current,16) <= 15:	
		something = something + "0" +current.replace("0x","")
	else:
		something = something + current.replace("0x","")
	print "res"
	print something
	data = [something]
	#data = ["4012FF"]
	send(data)
	print "digital Write end"


def digitalRead(pinNumber):
	temp = readInput()
	#pins = int(temp[2:4],16)
	pins = temp[2]
	pinNumber = pinTranslation(pinNumber)
	result = pins & pinNumber
	if result:
		pin =0
	else:
		pin = 1
	return pin


def readOutput():
	data = ["4112ff"]
	result = send(data)
	print "output read"
	print result
	return result


def readInput():
	data = ["4113ff"]
	result = send(data)
	return result




a = spi.SPI(0,0)
print "PY: initialising SPI mode, reading data, reading length . . . \n"




#pin1 = digitalRead(1)
#pin2 = digitalRead(2)
#pin3 = digitalRead(3)
#pin4 = digitalRead(2)
#print pin4
#print "Pin 1= {0}".format(pin1)
#print "Pin 2= {0}".format(pin2)
#print "Pin 3= {0}".format(pin3)
#print "Pin 4= {0}".format(pin4)




#digitalRead(1)
#digitalWrite(2,1)
#digitalWrite(2,1)
digitalWrite(1,1)
sleep(5)
digitalWrite(1,0)
sleep(5)
digitalWrite(1,1)
sleep(5)
digitalWrite(1,0)

#At the end of your program close the SPI port 	
a.close()






"""










#Python example for SPI bus, written by Brian Hensley
#This script will take any amount of Hex values and determine
#the length and then transfer the data as a string to the "spi" module

import spi
from time import sleep

#At the beginning of the program open up the SPI port.
#this is port /dev/spidevX.Y
#Being called as as spi.SPI(X,Y)
a = spi.SPI(0,0)

#print "PY: initialising SPI mode, reading data, reading length . . . \n"

#This is my data that I want sent through my SPI bus
#data = ["400A084000004012ff4001ff411300"]
#data = ["400dff"]# pullups enabled
data = ["4012FF"]
#data = ["4113ff"]
#data = ["401200"]

#Calculates the length, and devides by 2 for two bytes of data sent.
length_data = len(data[0])/2

#transfers data string
#print 'Value transfered to C spimodule:',data
print a.transfer(data[0], length_data)
	
#At the end of your program close the SPI port 	
a.close()

"""




