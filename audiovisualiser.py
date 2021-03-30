#!/usr/bin/env python

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import random
import pyaudio
import numpy as np

# Configuration
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # regular // adafruit-hat // adafruit-hat-pwm

colourchg=32 # how much colours will change by

rotateresample=Image.BICUBIC # Method for rotating image:  PIL.Image.NEAREST (fastest) // PIL.Image.BILINEAR // Image.BICUBIC

audiodevice=0 # Audio input device to use (see list generated at startup)

# Init Audio
audiobuffer=1024 
p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
	dev = p.get_device_info_by_index(i)
	print p.get_device_info_by_index(i)['index'],p.get_device_info_by_index(i)['name']
stream=p.open(format=pyaudio.paInt16,channels=1,input_device_index=audiodevice,rate=44100,input=True,frames_per_buffer=audiobuffer)

# Init Matrix
maxx=options.rows-1
maxy=options.cols-1
matrix = RGBMatrix(options = options)

# Init PIL
image = Image.new("RGB", (64, 64))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(image)  # Declare Draw instance before prims

colour=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
border=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)

# Random colour changing function
def colourchange(colour):
	i=random.randrange(0,3)
	clist=list(colour)
	if (random.randrange(0,2)==1):
		clist[i]=clist[i]+colourchg
	else:
		clist[i]=clist[i]-colourchg
	if clist[i]<32:
		clist[i]=32
	if clist[i]>255:
		clist[i]=255
	return (clist[0],clist[1],clist[2])

# Main loop
while True:
	# Read some data from input
	data = np.fromstring(stream.read(audiobuffer,exception_on_overflow=False),dtype=np.int16)
	# find peaks
	peak=np.average(np.abs(data))*2

	# cnt is our main reference for volume and should be somewhere between 0-32
	cnt=int(50*peak/2**16)
	if cnt<0:
		cnt=1
		
	# Change colours
	colour=colourchange(colour)
	border=colourchange(border)

	if random.randrange(0,20)>18 or cnt<8:
		draw.rectangle( (0,0,maxx,maxy),fill=(0,0,0)) # Clear screen
	
	if random.randrange(0,2)==1:
		# Draw a square
		draw.rectangle( ( (maxx/2)-cnt,(maxx/2)-cnt,(maxx/2)+cnt,(maxx/2)+cnt),colour,border,random.randrange(1,32) ) 
	else: 
		# Draw a circle
		draw.arc( ( (maxx/2)-cnt,(maxx/2)-cnt,(maxx/2)+cnt,(maxx/2)+cnt),0,360,colour,random.randrange(1,32) ) 
	
	# Rotate image
	image2=image.rotate(random.randrange(0,360),resample=rotateresample)
	
	# Display image on matrix
	matrix.SetImage(image2, 0, 0,True)

	# slow things down just a little
	time.sleep(.05)


