from time import sleep
from time import strftime
from picamera.array import PiRGBArray
from picamera import PiCamera
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import math
from math import acos
from math import asin
from math import atan
from math import degrees
import time
import RPi.GPIO as GPIO
import scipy
import datetime
import serial
import re
import os
import csv
import shutil
import glob
import threading


import numpy as np
import cv2
import socket
import urllib.request


lines = ("/home/pi/CWM_DATA/box.jpg")
post_process_FN = ("/home/pi/CWM_DATA/bxx.png")


# open video0
cap = cv2.VideoCapture(0)
# The control range can be viewed through v4l2-ctl -L
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
cap.set(38,3)     # would love to set buffsize to 1 ,,  but 3 is as low as it goes ???
os.system("v4l2-ctl -c exposure=20")               # exposure values min=006 max=906 default=800    higher number = longer exposure  doi!


#camera.resolution = (1024, 768)
frame = np.empty((768, 1024, 1), dtype=np.uint8)
frame1 = np.empty((768, 1024, 1), dtype=np.uint8)
gray = np.empty((768, 1024, 1), dtype=np.uint8)
imagex = np.empty((768, 1024, 1), dtype=np.uint8)

keepingon = 1

while(keepingon):
	k=0
	while k<4:
		ret, frame = cap.read() 
		k = k+1
	gray = cv2.GaussianBlur(frame, (11,11), 0)
	cv2.imshow('Before blur', frame)
	cv2.imshow('after blur', gray)
	cv2.imwrite((lines),gray)
	
	im = Image.open(lines) # Can be many different formats.
	pix = im.load()
	thresh = 75
	fn = lambda x : 255 if x > thresh else 0
	r = im.convert('L').point(fn, mode='1')
	pix = r.load()
	r.save(post_process_FN)
	
	imagex = cv2.imread(post_process_FN,0)
	cv2.imshow('after threshold', imagex)
	
	kkey = cv2.waitKey(1)
	if kkey == 27: 
		keepingon = 0
	
cap.release()
cv2.destroyAllWindows()
