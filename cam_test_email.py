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


import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

lines = ("/home/pi/CWM_DATA/box.jpg")
lines1= ("/home/pi/CWM_DATA/blx.jpg")
post_process_FN = ("/home/pi/CWM_DATA/bxx.png")

fromaddr = "cwm.sn.1021@gmail.com"
toaddr = "sargentw@gmail.com"
password = "qoiasyxzcoytkvtf"


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
	cv2.imwrite((lines1),frame)
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
		

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "test images"


body = "Test Images"


now = datetime.datetime.now()
buf = (now.strftime("%Y-%m-%d %H:%M:%S"))
body  = body + buf



msg.attach(MIMEText(body, 'plain'))

filename = lines1     
attachment = open(lines1, "rb")   
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

filename = lines  #"/home/pi/CWM_DATA/link_images.zip"
attachment = open(lines, "rb")
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

filename = post_process_FN  #destz   #"/home/pi/CWM_DATA/cfg.txt"  *or*   = destz
attachment = open(post_process_FN, "rb")      #destz
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, password)
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()

	
cap.release()
cv2.destroyAllWindows()
