import random
import Tkinter
from Tkinter import *
top = Tkinter.Tk()
top.minsize(300,300)
top.geometry("500x500")
top.title('piface Emulator')



HIGH = 1
LOW = 0
INPUT = 1
OUTPUT = 0


inputPins = 0
outputPin = 0

pinModes = 0

inputButtonArray =[]
outputButtonArray =[]

def pinTranslation(pin):
	return 2**(pin-1)


def readPin(pin):
	checkPinMode(pin, INPUT)
	global inputPins
	print 'Read of pin {}'.format(pin)
	pin = pinTranslation(pin)

	pin = pin & inputPins
	if pin:
		pin = 1

	print pin
	return pin


def writePin(pin,status):
	checkPinMode(pin, OUTPUT)
	global outputPins
	pin = pinTranslation(pin)
	if status:
		outputPins = outputPins | pin
	else:
		pin = ~pin
		outputPins = outputPins & pin

        print 'Output pins {}'.format(outputPins)


def physicallyChangePin(pin,status):
	global inputPins
	checkPinMode(pin, INPUT)
	pin = pinTranslation(pin)

	if status:
		inputPins = inputPins | pin
	else:
		inputPins = intputPins & ~pin

	print "Input pins"
	print inputPins

def checkPinMode(pin, intendedMode):
	global pinModes
	pin = pinTranslation(pin)
	if intendedMode:
		if not(pin & pinModes):
			print "exception"
		
	else:
		if pinModes & ~pin:
			print "exception"

	
def setPinMode(pin, mode):
	global pinModes
	
	pin = pinTranslation(pin)
	if mode ==INPUT:
		pinModes = pinModes | pin
		B =Tkinter.Checkbutton(top, text = pin, command = physicallyChangePin(1,HIGH))
		inputButtonArray.append(B)
	else:
		pinModes = pinModes & ~pin
		B =Tkinter.Checkbutton(top, text =pin, state=DISABLED)

		
		
		
def writeByte(pin, SBFIRST, data):
	print "nothing"


def readByte(pin, SBFIRST):
	print "nothing"

def setAllOutput(status):
	mask = 1
	count = 1
	while mask < 1000:
		if not(mask & pinModes):
			writePin(count, status)
		count+=1

def checkAllInput():
	if inputPins:
		return 1
	else
		return 0



B =Tkinter.Checkbutton(top, text = "Pin 1", command = physicallyChangePin(1,HIGH))
outputButtonArray.append(B)
B =Tkinter.Checkbutton(top, text = "Pin 2", command = physicallyChangePin(1,HIGH))
# B["text"]="no"
outputButtonArray.append(B)
print "hello"



for i,b in enumerate(outputButtonArray):
	b.pack()
	b.grid(row=0,column=i)
	print b


#B1 = Tkinter.Button(top, text = "Hello", command = physicallyChangePin(1,HIGH)).pack(side=LEFT)
#B2 = Tkinter.Button(top, text="On", command = physicallyChangePin(2,HIGH)).pack(side=LEFT)



top.mainloop()


