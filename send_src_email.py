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




		

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = "source files"


body = "Test Images"


now = datetime.datetime.now()
buf = (now.strftime("%Y-%m-%d %H:%M:%S"))
body  = body + buf



msg.attach(MIMEText(body, 'plain'))

filename = "/home/pi/mu_code/measureGS.py"    
attachment = open(filename, "rb")   
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

filename = "/home/pi/Linux-Client/src/main.cpp"
attachment = open(filename, "rb")
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)

filename = "/home/pi/CWM_DATA/cfg.txt"  
attachment = open(filename, "rb")     
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


cv2.destroyAllWindows()
