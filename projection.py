#import pygame
import numpy as np
from math import *
from PIL import Image
from PIL import ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import random
import time
import pyaudio
from pprint import pprint
from PIL import ImageFilter

# Init Audio
audiobuffer=64
audiodevice=0 # Audio input device to use (see list generated at startup)
p=pyaudio.PyAudio()
for i in range(p.get_device_count()):
	dev = p.get_device_info_by_index(i)
	print p.get_device_info_by_index(i)['index'],p.get_device_info_by_index(i)['name']
stream=p.open(format=pyaudio.paInt16,channels=1,input_device_index=audiodevice,rate=44100,input=True,frames_per_buffer=audiobuffer)


# Configuration
options = RGBMatrixOptions()
options.rows = 64
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.hardware_mapping = 'adafruit-hat-pwm'  # regular // adafruit-hat // adafruit-hat-pwm
matrix = RGBMatrix(options = options)
image = Image.new("RGB", (64, 64))  # Can be larger than matrix if wanted!!
draw = ImageDraw.Draw(image)  # Declare Draw instance before prims
colourchg=32 # how much colours will change by
WIDTH, HEIGHT = 64,64
maxnodesize=16
nodestyle=0
linestyle=0
colour=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
border=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
drawlines=True
drawnodes=False
colour=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
border=random.randrange(0,255),random.randrange(0,255),random.randrange(0,255)
scale = 20
filterlist=(ImageFilter.BLUR, ImageFilter.CONTOUR, ImageFilter.DETAIL, ImageFilter.EDGE_ENHANCE, ImageFilter.EDGE_ENHANCE_MORE,ImageFilter.EMBOSS, ImageFilter.FIND_EDGES, ImageFilter.SMOOTH, ImageFilter.SMOOTH_MORE, ImageFilter.SHARPEN)
nodestylelist=(0,1,2,3,4,5)
linestylelist=(0,1)
circle_pos = [WIDTH/2, HEIGHT/2]  # x, y
curfilter=2
angle = 0
linewidth=1
points = []

# all the cube vertices
points.append(np.matrix([-1., -1., 1.]))
points.append(np.matrix([1., -1., 1.]))
points.append(np.matrix([1.,  1., 1.]))
points.append(np.matrix([-1., 1., 1.]))
points.append(np.matrix([-1., -1., -1.]))
points.append(np.matrix([1., -1., -1.]))
points.append(np.matrix([1., 1., -1.]))
points.append(np.matrix([-1., 1., -1.]))


projection_matrix = np.matrix([
	[1, 0, 0],
	[0, 1, 0]
])


projected_points = [
	[n, n] for n in range(len(points))
]



def connect_points(i, j, points):
	if drawlines:
		if linestyle==0:
			draw.polygon( (points[i][0], points[i][1], points[j][0], points[j][1]), colourchange(colour), linewidth )
		elif linestyle==1:
			draw.line( (points[i][0], points[i][1], points[j][0], points[j][1]), colourchange(colour), linewidth )

	
# Random colour changing function
def colourchange(colour):
	i=random.randrange(0,3)
	clist=list(colour)
	if (random.randrange(0,2)==1):
		clist[i]=clist[i]+colourchg
	else:
		clist[i]=clist[i]-colourchg
	if clist[i]<0:
		clist[i]=0
	if clist[i]>255:
		clist[i]=255
	return (clist[0],clist[1],clist[2])


#clock = pygame.time.Clock()
factor=1.0
nodesize=0
lasttime=time.time()
while True:
	data = np.fromstring(stream.read(audiobuffer,exception_on_overflow=False),dtype=np.int16)
	peak=np.average(np.abs(data))*2
	# cnt is our main reference for volume and should be somewhere between 0-32
	cnt=int(50*peak/2**16)
	if cnt<0:
		cnt=0
	scale=(cnt/2)+4
	if scale<1:
		scale=1


	colourchg=cnt/2
	draw.rectangle( (0,0,64,64),fill=(0,0,0)) # Clear screen
	colour=colourchange(colour)
	border=colourchange(border)
	
	if random.randint(0,100)==1:
		curfilter=random.randrange(len(filterlist))
	
	if random.randint(0,100)==1:
		if drawlines==True:
			drawlines=False
		else:
			drawlines=True
	if random.randint(0,100)==1:
		if drawnodes==True:
			drawnodes=False
		else:
			drawnodes=True
	if drawnodes==False and drawnodes==False:
		drawnodes=True
		
	if random.randint(0,50)==1:
		linewidth=linewidth+random.randint(-1,1)
	if linewidth<1:
		linewidth=1
	if linewidth>4:
		linewidth=4

	nodesize=nodesize+random.uniform(-.5,.5)
	if nodesize<1:
		nodesize=1
	if nodesize>maxnodesize:
		nodesize=maxnodesize
	nodesize=cnt/4
		
	if random.randint(0,50)==1:
		nodestyle=random.randrange(len(nodestylelist))

	if random.randint(0,50)==1:
		linestyle=random.randrange(len(linestylelist))

	factor=factor+random.uniform(-.01,.01)
	if factor<.1:
		factor=.1
	if factor>2:
		factor=2

	rotation_z = np.matrix([
		[cos(angle), -sin(angle), 0],
		[sin(angle), cos(angle), 0],
		[0, 0, factor],
	])

	rotation_y = np.matrix([
		[cos(angle), 0, sin(angle)],
		[0, factor, 0],
		[-sin(angle), 0, cos(angle)],
	])

	rotation_x = np.matrix([
		[factor, 0, 0],
		[0, cos(angle), -sin(angle)],
		[0, sin(angle), cos(angle)],
	])
	angle += .1



	i = 0

		
	for point in points:
		rotated2d = np.dot(rotation_z, point.reshape((3, 1)))
		rotated2d = np.dot(rotation_y, rotated2d)
		rotated2d = np.dot(rotation_x, rotated2d)

		projected2d = np.dot(projection_matrix, rotated2d)

		x = int(projected2d[0][0] * scale) + circle_pos[0]
		y = int(projected2d[1][0] * scale) + circle_pos[1]

		projected_points[i] = [x, y]
		if drawnodes:
			if nodestyle==0:
				draw.chord( (x-nodesize,y-nodesize,x+nodesize,y+nodesize), 0,360, fill=colourchange(border),width=1,outline=colourchange(colour) ) 
			elif nodestyle==1:
				draw.chord( (x-nodesize,y-nodesize,x+nodesize,y+nodesize), 0,360, fill=colourchange(border),width=1 ) 
			elif nodestyle==2:
				draw.chord( (x-nodesize,y-nodesize,x+nodesize,y+nodesize), 0,360, width=1,outline=colourchange(colour) ) 
			elif nodestyle==3:
				draw.rectangle( (x-nodesize,y-nodesize,x+nodesize,y+nodesize),width=1,outline=colourchange(colour) ) 
			elif nodestyle==4:
				draw.rectangle( (x-nodesize,y-nodesize,x+nodesize,y+nodesize),width=1,fill=colourchange(border),outline=colourchange(colour) ) 
			elif nodestyle==5:
				draw.chord( (x-nodesize,y-nodesize,x+nodesize,y+nodesize), 0,360, fill=colourchange(border),width=1,outline=(0,0,0) ) 
		
		i += 1

	for p in range(4):
		connect_points(p, (p+1) % 4, projected_points)
		connect_points(p+4, ((p+1) % 4) + 4, projected_points)
		connect_points(p, (p+4), projected_points)
	
	image2=image.filter(filterlist[curfilter])
		
	matrix.SetImage(image2, 0,0, True)
	
	if time.time()-lasttime>2:
		print "nodestyle:",nodestyle,"linestyle:",linestyle,"nodesize:",int(nodesize),"linewidth:",linewidth,"drawnodes:",drawnodes,"drawlines:",drawlines,"filter:",curfilter
		lasttime=time.time()
	
	time.sleep(.07)
	
