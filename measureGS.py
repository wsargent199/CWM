
#!/usr/bin/python3
### BEGIN INIT INFO
# Provides: measureGS.py
# Required-Start: $remote_fs $syslog
# Required-Stop: $remote_fs $syslog
# Default-Start: 2 3 4 5
# Default-Stop: 0 1 6
# Short-Description: link measure
# Description:
### END INIT INFO
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
#import imutils
import datetime
import serial
import re
import os
import csv
import shutil
import glob
import threading

from zipfile import ZipFile
from os import path
from os.path import basename
from scipy.spatial import distance as dist
#from imutils import perspective
#from imutils import contours


import numpy as np
import cv2
import socket
import urllib.request

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

send_stuff = "/tmp/my_fifo"
send_timestamps = "/tmp/my_fifo1"
rx_commands = "/tmp/my_fifo2"

link_cnt_1 = 0;
link_cnt_2 = 0;
link_cnt_3 = 0;
link_cnt_4 = 0;
link_cnt_5 = 0;

link_cnt_1_ts = '      ';
link_cnt_2_ts = '      ';
link_cnt_3_ts = '      ';
link_cnt_4_ts = '      ';
link_cnt_5_ts = '      ';
saved_TS      = '      ';
c_time        = '      '; 

font = ImageFont.truetype("/home/pi/mu_code/fontsx/bodoni/BodoniFLF-Bold.ttf", 20)

survey_state = 0      # idle at startup for now       
off_cycles   = 1
last_pin_rd  = 0

hack_offset = 0;



#   survey_state meanings
#     0 = idle
#     1 = armed           waiting for link 1 occure and start a survey 
#     2 = in_progress     survey happenen
#     3 = completed       survey completed ..  email send in progress
#     ** after email and house keeping done return to idle (0) **
#

#camera = PiCamera(resolution=(1024, 768), framerate=(60))
#millisec = int(round(time.time() * 1000))   # take time snapshot
# open video0
cap = cv2.VideoCapture(0)
# The control range can be viewed through v4l2-ctl -L
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 800)
cap.set(38,3)     # would love to set buffsize to 1 ,,  but 3 is as low as it goes ???
os.system("v4l2-ctl -c exposure=400")               # exposure values min=006 max=906 default=800    higher number = longer exposure  doi!
#millisec1 = int(round(time.time() * 1000))   # take time snapshot
#print (" VideoCap init complete ",(millisec1 - millisec))



MyDateTime = datetime.datetime(2016,1,3,8,30,20)

#honda_FN  = "asdfghjkl"

counter=0
first_cycle = 1





def connect(host='http://google.com'):
    try:
        urllib.request.urlopen(host) #Python 3.x
        return True
    except:
        return False


def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# Zip the files from given directory that matches the filter
def zipFilesInDir(dirName, zipFileName, filter):
   # create a ZipFile object
   with ZipFile(zipFileName, 'w') as zipObj:
       # Iterate over all the files in directory
       for folderName, subfolders, filenames in os.walk(dirName):
           for filename in filenames:
               if filter(filename):
                   # create complete filepath of file in directory
                   filePath = os.path.join(folderName, filename)
                   # Add file to zip
                   zipObj.write(filePath, basename(filePath))
                   
                   


debug = 1
millisec = 1000
millisec1 = 1000
one_shot = 0
doodle = 0
detect_circles = 0
x=100
y=100
tran = 0
lst_tran = 0
y_right = 0
y_left = 0
value = 0,0,0
value_black = 0,0,0
value_white =255,255,255
value_mid = 127,127,127
value_ppp = 0,0,0
idx_x = 0
idx_y = 0
resolution_x = 1024
resolution_y = 768
first_top_bar = 0
top_bar = 0
middle_bar = 0
bottom_bar = 0
last_middle_bar = 0
last_good_rt_scan = 0
last_good_lft_scan = 0
last_sensor = 0
last_sensor_up = 0
last_sensor_down = 0
w = 1
last_w = 1
image_stream = 0
zed = 0
new_frame=0
sequence = 0
file_rec_count = 0
alarm_list = " \r"
link_data = 0,0,0,0
scan_results = [[0,0,0,0,0]]
for i in range(1280):
        scan_results.append([0,0,0,0,0])
        
now = datetime.datetime.now()
buf = (now.strftime("%Y-%m-%d %H:%M:%S"))

# load default values in case there is no cfg.csv file   ** and create the variable ..  maybe nesc / maybe not,  python confuses me
chain_name = "TP2"
BaseLine_File_Name = "TP2_baseline.csv"
output_file_name = "resultx.csv"
output_file_type = "delta"
stretch_limit = "0.0125"
paint_enable = "no"
create_baseline = "no"
this_baseline_len = 2.500
chain_direction = 'rtl'
send_email = 'yes'
fromaddr = "cwm.sn.1021@gmail.com"
toaddr = "sargentw@gmail.com;wsargent199@yahoo.com"
password = "digilube1021"
off_cycles_cfg = "1000"
downstream = "10"



GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
GPIO.setup(40,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(38,GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(36,GPIO.IN, pull_up_down=GPIO.PUD_UP)

GPIO.setup(11, GPIO.OUT)
GPIO.setup(12, GPIO.OUT)

GPIO.setup(37, GPIO.OUT)


GPIO.output(37, GPIO.HIGH)


#camera.resolution = (1024, 768)
frame = np.empty((768, 1024, 1), dtype=np.uint8)
frame1 = np.empty((768, 1024, 1), dtype=np.uint8)
gray = np.empty((768, 1024, 1), dtype=np.uint8)
imagex = np.empty((768, 1024, 1), dtype=np.uint8)


test_char = 'x'
test_val = 123



ser = serial.Serial(
 port='/dev/ttyS0',
 baudrate = 115200,
 parity = serial.PARITY_NONE,
 stopbits=serial.STOPBITS_ONE,
 bytesize=serial.EIGHTBITS
)

ser.timeout = None

print ('local serial port test successful')
serial_port_type = 'hardwire'
print ('hardwire')



ser.write(bytes(" waiting for pipes  \r",'UTF-8'))
while (os.path.exists('/tmp/my_fifo')==0) or (os.path.exists('/tmp/my_fifo1')==0) or (os.path.exists('/tmp/my_fifo2')==0):
    print("waiting for pipes to be created")
    time.sleep(1) # Sleep for 1 seconds


pipe_fifo  = os.open(send_stuff, os.O_WRONLY)
pipe_fifo1 = os.open(send_timestamps, os.O_WRONLY)
pipe_fifo2 = os.open(rx_commands, os.O_RDONLY | os.O_NONBLOCK)


ser.write(bytes(" RPi boot OK        \r",'UTF-8'))

#thumb_name = []
#while thumb_name == []:
#    sleep(1)
#    thumb_name = os.listdir("/media/pi")
#    if (debug == 1):
        #ser.write(bytes("usb drv not detected\r",'UTF-8'))
#        print ("USB thumb drv name > ",thumb_name)


#thumb_name_pure = thumb_name[0]

#ser.write(bytes("usb drv detected    \r",'UTF-8'))

#buf10 = "False"
#while buf10 == 'False':
#    buf10 = (str(path.exists("/media/pi/" + thumb_name_pure + "/CWM/cfg.txt")))
#    sleep(1)
    #ser.write(bytes("cfg.txt not detected\r",'UTF-8'))

#ser.write(bytes(" reading cfg.txt    \r",'UTF-8'))
#with open("/media/pi/" + thumb_name_pure + "/CWM/cfg.txt", 'r') as reader:
with open("/home/pi/CWM_DATA/cfg.txt", 'r') as reader:

    #read the chain name line
    buf10 = reader.readline()                       # read entire line
    chain_name = buf10[21:(len(buf10)-1)]             # cut out just the chain_name

    if (debug == 1):
        print("chain name > ",chain_name)

    #read the baseline file name line
    buf10 = reader.readline()                       # read entire line
    BaseLine_File_Name = buf10[21:(len(buf10)-1)]     # cut out just the baseline file name part

    if (debug == 1):
        print("BaseLine File Name > ",BaseLine_File_Name)

    #read the output file name line
    buf10 = reader.readline()                       # read entire line
    output_file_name = buf10[21:(len(buf10)-1)]       # cut out just the output file name part

    if (debug == 1):
        print("output file name > ", output_file_name)

    #read the output file type line
    buf10 = reader.readline()                       # read entire line
    output_file_type = buf10[21:(len(buf10)-1)]       # cut out just the output file type part

    if (debug == 1):
        print("output file type > ",output_file_type)

    #read the stretch limit line
    buf10 = reader.readline()                       # read entire line
    stretch_limit = buf10[21:(len(buf10)-1)]       # cut out just the stretch limit part

    if (debug == 1):
        print("stretch_limit) > ",stretch_limit)

    #read the paint enable line
    buf10 = reader.readline()                       # read entire line
    paint_enable = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("paint_enable > ",paint_enable)

    #read the create baseline line
    buf10 = reader.readline()                       # read entire line
    create_baseline = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("create_baseline > ",create_baseline)

    if create_baseline == "yes" :
        output_file_type = "absolute"
        paint_enable = "no"

    #read the chain direction line
    buf10 = reader.readline()                       # read entire line
    chain_direction = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("chain direction > ",chain_direction)

    #read the send email line
    buf10 = reader.readline()                       # read entire line
    send_email = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("send_email > ",send_email)

    #read the destination address line
    buf10 = reader.readline()                       # read entire line
    toaddr = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("to address > ",toaddr)

    #read the origin address line
    buf10 = reader.readline()                       # read entire line
    fromaddr = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("from addr > ",fromaddr)

    #read the email password line
    buf10 = reader.readline()                       # read entire line
    password = buf10[21:(len(buf10)-1)]       # cut out yes/no part

    if (debug == 1):
        print("password > ",password)
        
    #read the off cycles line
    buf10 = reader.readline()                      # read entire line
    off_cycles_cfg = buf10[21:(len(buf10)-1)]      # cut out just the stretch limit part
    this_off_cycle = int(off_cycles_cfg)

    if (debug == 1):
        print("off cycles > ",this_off_cycle)
        
    #read the downstream line
    buf10 = reader.readline()                      # read entire line
    downstream = buf10[21:(len(buf10)-1)]          # cut out just the stretch limit part
    this_downstream = int(downstream)

    if (debug == 1):
        print("downstream > ",this_downstream)       
                


#filenamex = "/media/pi/" + thumb_name_pure + "/CWM/"     #results_%d.csv" % (sequence)
filenamex = "/home/pi/CWM_DATA"
filenamey = str(BaseLine_File_Name)
filenamez = ".csv"
filenamebaseline = filenamex + filenamey + filenamez

#print (filenamebaseline)

#print (str(path.exists(filenamebaseline)))

baseline_buf = "0.001"
counter = 0
baseline_data = ["0.001"]
while counter < 10000 :
    baseline_data.append(baseline_buf)
    counter = counter + 1


if str(path.exists(filenamebaseline))=="True":
    with open(filenamebaseline) as byte_reader:
        counter = 0
        baseline_buf = "xxxx"
        crap = "xxxx"
        while baseline_buf != '' :
            baseline_buf = byte_reader.read(5)
            baseline_data[counter] = (baseline_buf)
            counter = counter+1
            crap = byte_reader.read(1)
            if crap == '':
                baseline_buf = crap
#else:
#    paint_enable = "no"

#ser.write(bytes(" link processed OK  \r",'UTF-8'))


ser.write(bytes(" usb drv detected   \r",'UTF-8'))
sleep(1)
ser.write(bytes(" Calibrating Camera \r",'UTF-8'))

ser.write(bytes("+\r",'UTF-8'))


# Set ISO to the desired value
#camera.iso = 1200
# Wait for the automatic gain control to settle
sleep(2)
ser.write(bytes("+\r",'UTF-8'))
# Now fix the values
#camera.shutter_speed = camera.exposure_speed
#camera.exposure_mode = 'off'
#g = camera.awb_gains
#camera.awb_mode = 'off'
#camera.awb_gains = g
# Finally, take several photos with the fixed settings
#camera.capture_sequence(['image%02d.jpg' % i for i in range(10)])
GPIO.output(37, GPIO.LOW)    # turn backlight off
ser.write(bytes("-\r",'UTF-8'))

if chain_direction == 'rtl':
        ser.write(bytes("a\r",'UTF-8'))

if chain_direction == 'ltr':
        ser.write(bytes("b\r",'UTF-8'))

ser.write(bytes("-\r",'UTF-8'))






ser.write(bytes(" waiting to connect \r",'UTF-8'))
while connect() == False:
    print('waiting to connect')
    time.sleep(1) # Sleep for 1 seconds
    
ser.write(bytes(" RPi ready          \r",'UTF-8'))

RPi_addr=([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

length_o_address=len(RPi_addr)
#print(length_o_address)

output = ''
i = length_o_address
while i < 20:
	RPi_addr += "*"
	i = i + 1


while(True):



    #print (RPi_addr)
    ser.write(bytes(RPi_addr + " \r",'UTF-8'))
    
    #if survey_state == 2:
        #millisec1 = int(round(time.time() * 1000)) 
        #print ("done3",(millisec1 - millisec))
        
    
    #if (pipe_fifo2 != -1):
    #    a_string = os.read(pipe_fifo2,5)
    #    print (a_string)

    k = 0
    millisec = int(round(time.time() * 1000)) 
    if survey_state == 2:
        ser.write(bytes("+\r",'UTF-8'))
    while k < 2:
        k = ser.in_waiting
        ret, frame = cap.read() 
        if survey_state == 2:
            millisec1 = int(round(time.time() * 1000)) 
            if ((millisec1 - millisec)>1000):
                millisec = int(round(time.time() * 1000)) 
                ser.write(bytes("+\r",'UTF-8'))
    a_string=ser.readline()
    
    
    print ("OFF CYCLES = ", off_cycles)
    ser.write(bytes("xxx3\r",'UTF-8'))    


    if off_cycles > 0:
        if GPIO.input(11):
            GPIO.output(11,GPIO.LOW)
            if last_pin_rd == 0:
                off_cycles = 99999
                last_pin_rd = 1
        else:
            last_pin_rd = 0;

    #length_o_address=len(a_string)
    #print(length_o_address)
    
    ser.write(bytes("!\r",'UTF-8'))

    if debug == 1:
            print ("from pic24 ? ",a_string)

    #millisec = int(round(time.time() * 1000))   # take time snapshot
    
    if survey_state == 2:
        ser.write(bytes("***processing link**\r",'UTF-8'))

    numbers = []


    buff11 = a_string[2:7]

    for word in buff11.split():
        if word.isdigit():
            numbers.append(int(word))
            w = int(word)

    if w == 1:
        if last_w > 580 and last_w < 585:
            hack_offset = last_w
        else:
            hack_offset = 0

    w = w + hack_offset



    test_payload = "*a%06d" % (w)
    os.write(pipe_fifo,test_payload.encode())

    print(test_payload)
    
    test_payload = "*g%06d" % (off_cycles)
    os.write(pipe_fifo,test_payload.encode())
    

    if (w==1):
        
        print ("survey_state = ", (survey_state))
        print ("  off_cycles = ", (off_cycles))
        
        if(survey_state == 3):  
            off_cycles = 1
            survey_state = 0            # if we have just finishedsend cycle ,,  restart cnting off cycles
        
        if(survey_state == 2):  
            survey_state = 3            # if we have just finished a survey then send the stuff 
        
        if(survey_state == 0):
            
            if (first_cycle == 1):
                first_cycle = 0
            else:
                off_cycles += 1
            if (off_cycles > this_off_cycle):         #   60  $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
                off_cycles = 0
                survey_state = 2        # go straight to survey in progress  ( armed reserved for dashboard frc survey button )
            
        if(survey_state == 1):  
            survey_state = 2            # if we were previously 'armed' then start survey  
        
        print ("survey_state = ", (survey_state))
        print ("  off_cycles = ", (off_cycles))
        
        
        #if (sequence == 0):
        #    saved_TS = (now.strftime("%Y-%m-%d %H:%M:%S"))

        if (sequence!=0):
            link_cnt_5 = link_cnt_4;
            link_cnt_4 = link_cnt_3;
            link_cnt_3 = link_cnt_2;
            link_cnt_2 = link_cnt_1;
            link_cnt_1 = (last_w);

            test_payload = "*b%06d" % (link_cnt_1)
            os.write(pipe_fifo,test_payload.encode())

            test_payload = "*c%06d" % (link_cnt_2)
            os.write(pipe_fifo,test_payload.encode())

            test_payload = "*d%06d" % (link_cnt_3)
            os.write(pipe_fifo,test_payload.encode())

            test_payload = "*e%06d" % (link_cnt_4)
            os.write(pipe_fifo,test_payload.encode())

            test_payload = "*f%06d" % (link_cnt_5)
            os.write(pipe_fifo,test_payload.encode())


            now = datetime.datetime.now()
            saved_TS = (now.strftime("%Y-%m-%d %H:%M:%S"))

            test_payload = "*a"
            test_payload = test_payload + saved_TS
            print (test_payload)
            os.write(pipe_fifo1,test_payload.encode())
            
            


            if(survey_state == 3):  # if survey just completed then prepare and send the data 
                
                
                test_payload = "*a%06d" % (777777)
                os.write(pipe_fifo,test_payload.encode())

                GPIO.output(12, GPIO.LOW)

                off_cycles = 1
            
                length_in = 0.001
                buf = "%1.3f\r\n" % (length_in)
                while file_rec_count < 10000:
                    fcsv.write(buf)
                    file_rec_count = file_rec_count+1
                fcsv.close()


                #zipFilesInDir('/home/pi/CWM_DATA/', zipfilename, lambda name : 'png' in name)
                zipFilesInDir('/mnt/ramdisk/', zipfilename, lambda name : 'png' in name)
                
                # Get a list of all the file paths that ends with .png in aspecified directory
                #fileList = glob.glob('/home/pi/CWM_DATA/*.png')
                fileList = glob.glob('/mnt/ramdisk/*.png')

                # Iterate over the list of filepaths & remove each file.
                for filePath in fileList:
                    try:
                        os.remove(filePath)
                    except:
                        #print("Error while deleting file : ", filePath)
                        nothing = 1

                # Get a list of all the file paths that ends with .jpg in aspecified directory
                #fileList = glob.glob('/home/pi/CWM_DATA/*.jpg')
                fileList = glob.glob('/mnt/ramdisk/*.jpg')
                # Iterate over the list of filepaths & remove each file.
                for filePath in fileList:
                    try:
                        os.remove(filePath)
                    except:
                        #print("Error while deleting file : ", filePath)
                        nothing = 1

                survey_state = 0
                off_cycles = 1

                if send_email == "yes":
                    msg = MIMEMultipart()
                    msg['From'] = fromaddr
                    msg['To'] = toaddr
                    msg['Subject'] = chain_name


                    body = "Chain_Name: "
                    buf = chain_name
                    body = body + buf
                    buf  = "\rData Sample ending at "
                    body = body + buf

                    now = datetime.datetime.now()
                    buf = (now.strftime("%Y-%m-%d %H:%M:%S"))

                    body  = body + buf

                    buf   = "\rObserved chain length = %d links\r" %(last_w)  #was (last_w-1)
                    body  = body + buf
                    buf   = "link exception list :\r"
                    body  = body + buf


                    body = body + alarm_list

                    msg.attach(MIMEText(body, 'plain'))

                    filename = csvfilename     
                    attachment = open(csvfilename, "rb")   
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((attachment).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                    msg.attach(part)

                    filename = zipfilename  #"/home/pi/CWM_DATA/link_images.zip"
                    attachment = open(zipfilename, "rb")
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((attachment).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                    msg.attach(part)

                    filename = destz                 #destz #"/home/pi/CWM_DATA/cfg.txt"  *or*   = destz
                    attachment = open(destz,"rb")    #("/home/pi/mu_code/measureGS.py", "rb")      #destz
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload((attachment).read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
                    msg.attach(part)

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(fromaddr, password)
                    text = msg.as_string()
                    print(toaddr)
                    recipients = ['sargentw@gmail.com','wsargent199@yahoo.com']
                    print(recipients)
                    #toaddr = recipients
                    print(toaddr)
                    server.sendmail(fromaddr, recipients, text)
                    server.quit()

                if send_email == "no":
                    #print ('send email = no')
                    #print (thumb_name_pure)

                    shutil.copyfile('/home/pi/CWM_DATA/link_images.zip', '/media/pi/' + thumb_name_pure + '/CWM/link_images.zip')
                    shutil.copyfile(csvfilename, '/media/pi/' + thumb_name_pure + '/CWM/result.csv')


                    body = "Chain_Name: "
                    buf = chain_name
                    body = body + buf

                    buf  = "\rData Sample ending at "
                    body = body + buf

                    now = datetime.datetime.now()
                    buf = (now.strftime("%Y-%m-%d %H:%M:%S"))

                    body  = body + buf

                    buf   = "\rObserved chain length = %d links\r" %(last_w)
                    body  = body + buf
                    buf   = "link exception list :\r"
                    body  = body + buf

                    body = body + alarm_list

                    summary_file = open('/media/pi/' + thumb_name_pure + '/CWM/summary.txt' , "w")
                    n = summary_file.write(body)
                    summary_file.close()
                    
                    ser.reset_input_buffer()

            if(survey_state == 2):  # if survey just starting then do the houskeeping to initialize
                
                # Get a list of all the file paths that ends with .png in aspecified directory
                fileList = glob.glob('/home/pi/CWM_DATA/*.png')

                # Iterate over the list of filepaths & remove each file.
                for filePath in fileList:
                    try:
                        os.remove(filePath)
                    except:
                        #print("Error while deleting file : ", filePath)
                        nothing = 1

                # Get a list of all the file paths that ends with .jpg in aspecified directory
                fileList = glob.glob('/home/pi/CWM_DATA/*.jpg')

                # Iterate over the list of filepaths & remove each file.
                for filePath in fileList:
                    try:
                        os.remove(filePath)
                    except:
                        #print("Error while deleting file : ", filePath)
                        nothing = 1


        #if sequence < 2:
        sequence = sequence+1

        if(survey_state == 2):  # if survey just starting then do the houskeeping to initialize
         

            sourcez = "/home/pi/CWM_DATA/cfg.txt"

   
            #filenamex = "/media/pi/" + thumb_name_pure + "/CWM/"
            #filenamex = "/home/pi/CWM_DATA/"
            filenamex = "/mnt/ramdisk/"
            filenamey = str(output_file_name)
            filenamez = "_%d.csv" % (sequence)
            filename = filenamex + filenamey + filenamez
            csvfilename = filename

            filenamezz = "_%d.zip" % (sequence)
            zipfilename = filenamex + filenamey +filenamezz
            
            filenameqq =  "_%d.cfg" % (sequence)
            destz = filenamex + filenamey + filenameqq

            shutil.copyfile(sourcez,destz)

            #print (filename)
            if create_baseline == "yes" :
                if sequence == 1 :
                    filename = filenamebaseline
            fcsv = open(filename, "w+")
            filenameoutput = filename
            alarm_list = " \r"              # initialize alarm list string
            length_in = 1


        file_rec_count = 0

    last_w = w
    if(survey_state == 2):  # if survey in progress then process linkski
        
        
        millisec = int(round(time.time() * 1000))   # take time snapshot
        print ("Start")

        #ret, frame = cap.read()
        
        millisec1 = int(round(time.time() * 1000))   # take time snapshot
        print ("VideoCap complete ",(millisec1 - millisec))

        ser.write(bytes("-\r",'UTF-8'))
        zed = zed+1
        gray = cv2.GaussianBlur(frame, (11,11), 0)

        #lines = ("/home/pi/CWM_DATA/box%d.jpg" % (w))
        lines = ("/mnt/ramdisk/box%d.jpg" % (w))
        new_frame = 2   # voodoo


        if (new_frame==2):
            new_frame=0

            post_process_FN = filename = ("/mnt/ramdisk/boo2_%d.png"  %(w))

            w = w + 1

            millisec1 = int(round(time.time() * 1000))   # take time snapshot
            print ("converted to gray",(millisec1 - millisec))

            #(thresh, blackAndWhiteImage) = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY)
            flipped = cv2.flip(gray,0)
            cv2.imwrite((lines),flipped)
            millisec1 = int(round(time.time() * 1000))   # take time snapshot
            print ("converted to b+w",(millisec1 - millisec))
            #cv2.imshow('Before blur', frame)
            #cv2.imshow('Black white image', gray)
            #cv2.waitKey(0)
            #cv2.destroyAllWindows()

            im = Image.open(lines) # Can be many different formats.

            
            pix = im.load()

            thresh = 225
            fn = lambda x : 255 if x > thresh else 0
            r = im.convert('L').point(fn, mode='1')
            pix = r.load()


            if image_stream < 10:
                image_stream += 1

            state = 0
            sub_state = 0
            idx_x = 640
            idx_y = 790
            #if ((image_stream == 10):   # should be 10 you know
            if (1):   
                while idx_x < resolution_x:
                    while idx_y > 20:    #idx_y < resolution_y:
                        #print ( idx_x,idx_y,first_top_bar,middle_bar,bottom_bar )
                        if state == 0:
                            if pix[idx_x,idx_y] > 127:
                                sub_state += 1
                                if sub_state > 25:
                                    state = 1
                                    top_bar = 0
                            else:
                                sub_state = 0
                            pix[idx_x,idx_y] = 0
                        elif state == 1:
                            if pix[idx_x,idx_y] > 127:
                                top_bar += 1
                            else:
                                if (pix[idx_x,idx_y] < 127) and (pix[idx_x,idx_y-1] < 127) and (pix[idx_x,idx_y-2] < 127) and (pix[idx_x,idx_y-3] < 127) and (pix[idx_x,idx_y-4] < 127) and (pix[idx_x,idx_y-5] < 127):
                                    state = 2
                                    first_top_bar = idx_y
                                    top_bar = 0
                                    sub_state = 0

                            if math.fmod(idx_x,4) == 0:
                                pix[idx_x,idx_y] = 0

                        elif state == 2:
                            if (pix[idx_x,idx_y] > 127) and (pix[idx_x,idx_y-1] > 127) and (pix[idx_x,idx_y-2] > 127) and (pix[idx_x,idx_y-3] > 127) and (pix[idx_x,idx_y-4] > 127) and (pix[idx_x,idx_y-5] > 127) and (pix[idx_x,idx_y-6] > 127) and (pix[idx_x,idx_y-7] > 127) and (pix[idx_x,idx_y-8] > 127):
                                state = 3
                                sub_state = 0
                                middle_bar = 0
                            else:
                                top_bar += 1
                            if math.fmod(idx_x,4) == 0:
                                pix[idx_x,idx_y] = 255
                        elif state == 3:
                            if pix[idx_x,idx_y] > 127:
                                middle_bar += 1
                            else:
                                if (pix[idx_x,idx_y-4] < 127) and (pix[idx_x,idx_y-1] < 127) and (pix[idx_x,idx_y-2] < 127) and (pix[idx_x,idx_y-3] < 127):
                                    state = 4
                                    bottom_bar = 0
                                    tran = idx_y
                                    if idx_x == 640:
                                        lst_tran = tran
                                    idx_y =  2           #resolution_y - 1
                            if math.fmod(idx_x,4) == 0:
                                pix[idx_x,idx_y] = 0

                        elif state == 4:
                            if pix[idx_x,idx_y] < 127:
                                bottom_bar += 1
                            else:
                                state = 5
                            if math.fmod(idx_x,4) == 0:
                                pix[idx_x,idx_y] = 255

                        elif state == 5:
                            pix[idx_x,idx_y] = 0
                        idx_y -= 1
                    #print (idx_x,idx_y,top_bar,middle_bar,bottom_bar )
                    scan_results[idx_x] = ([idx_x,top_bar,middle_bar,bottom_bar,tran])
                    idx_x += 1
                    if (tran >(lst_tran+5)) or (tran <(lst_tran+-5)):
                        idx_x = resolution_x+1
                    else:
                        lst_tran = tran
                        last_good_rt_scan = idx_x - 4
                #	state = 0
                #	idx_y = 0

                    state = 1
                    idx_y = first_top_bar + 20
                    
                    
            state = 0
            sub_state = 0
            idx_x = 639
            idx_y = 790
            #idx_x = 5
            millisec1 = int(round(time.time() * 1000)) 
            print ("donehlf",(millisec1 - millisec))
            
            while idx_x > 20:
                while idx_y > 20:
                    if state == 0:
                        if pix[idx_x,idx_y] > 127:
                            sub_state += 1
                            if sub_state > 25:
                                state = 1
                                top_bar = 0
                        else:
                            sub_state = 0
                        if math.fmod(idx_x,4) == 0:
                            pix[idx_x,idx_y] = 0
                    elif state == 1:
                        if pix[idx_x,idx_y] > 127:
                            top_bar += 1
                        else:
                            if (pix[idx_x,idx_y] < 127) and (pix[idx_x,idx_y-1] < 127) and (pix[idx_x,idx_y-2] < 127) and(pix[idx_x,idx_y-3] < 127):
                                state = 2
                                first_top_bar = idx_y
                                top_bar = 0
                                sub_state = 0
                        if math.fmod(idx_x,4) == 0:
                            pix[idx_x,idx_y] = 0

                    elif state == 2:
                        if (pix[idx_x,idx_y] > 127) and (pix[idx_x,idx_y-1] > 127) and (pix[idx_x,idx_y-2] > 127) and (pix[idx_x,idx_y-3] > 127) and (pix[idx_x,idx_y-4] > 127) and (pix[idx_x,idx_y-5] > 127) and (pix[idx_x,idx_y-6] > 127) and (pix[idx_x,idx_y-7] > 127) and (pix[idx_x,idx_y-8] > 127):
                            state = 3
                            sub_state = 0
                            middle_bar = 0
                        else:

                            top_bar += 1
                        if math.fmod(idx_x,4) == 0:
                            pix[idx_x,idx_y] = 255
                    elif state == 3:
                        if pix[idx_x,idx_y] > 127:
                            middle_bar += 1
                        else:
                            if (pix[idx_x,idx_y] < 127) and (pix[idx_x,idx_y-1] < 127) and (pix[idx_x,idx_y-2] < 127) and (pix[idx_x,idx_y-3] < 127) and (pix[idx_x,idx_y-4] < 127):
                                state = 4
                                bottom_bar = 0
                                tran = idx_y
                                if idx_x == 639:
                                    lst_tran = tran
                                last_middle_bar = middle_bar
                                idx_y = 10
                        if math.fmod(idx_x,4) == 0:		
                            pix[idx_x,idx_y] = 00

                    elif state == 4:
                        if pix[idx_x,idx_y] < 127:
                            bottom_bar += 1
                        else:
                            state = 5
                        if math.fmod(idx_x,4) == 0:
                            pix[idx_x,idx_y] = 255

                    elif state == 5:
                        pix[idx_x,idx_y] = 0

                    idx_y -= 1
                    
                scan_results[idx_x] = ([idx_x,top_bar,middle_bar,bottom_bar,tran])
                idx_x -= 1
                if (tran >(lst_tran+5)) or (tran <(lst_tran+-5)) or (middle_bar > (last_middle_bar+5)) or (middle_bar < (last_middle_bar-5)):
                    idx_x = 10
                else:
                    lst_tran = tran
                    last_middle_bar = middle_bar
                    last_good_lft_scan = idx_x + 4

                state = 1
                idx_y = first_top_bar + 20

            millisec1 = int(round(time.time() * 1000))     
            print ("done processing",(millisec1 - millisec))


            y_left = scan_results[last_good_lft_scan][4]
            y_left += (scan_results[last_good_lft_scan][2]/2)

            y_right = scan_results[last_good_rt_scan][4]
            y_right += (scan_results[last_good_rt_scan][2]/2)

            draw = ImageDraw.Draw(r)
            draw.line((last_good_lft_scan,y_left,last_good_rt_scan,y_right), fill = 255, width = 60)
            draw.line((last_good_lft_scan,y_left,last_good_rt_scan,y_right), fill = 0, width = 3)

            draw.line((last_good_lft_scan,y_left,last_good_lft_scan+10,y_left+10), fill = 0, width = 3)
            draw.line((last_good_lft_scan,y_left,last_good_lft_scan+10,y_left-10), fill = 0, width = 3)


            draw.line((last_good_rt_scan,y_right,last_good_rt_scan-10,y_right+10), fill = 0, width = 3)
            draw.line((last_good_rt_scan,y_right,last_good_rt_scan-10,y_right-10), fill = 0, width = 3)
            
            millisec1 = int(round(time.time() * 1000)) 
            print ("donea",(millisec1 - millisec))

            lth = last_good_rt_scan -last_good_lft_scan
            length_in = lth * .0095
            buf = "% 1.3f inch" % (length_in)
            #print (buf)

            #buf1 = "%1.3f\r\n" % (length_in)
            #if (sequence!=0):
            #    fcsv.write(buf1)
            #    file_rec_count = file_rec_count+1


            draw.line((90,90,350,90), fill = 0, width = 150)   #in from right , down from top


            #draw.text((last_good_lft_scan+10,y_left+10), buf, fill = (0))
            ImageDraw.Draw(r).text((last_good_lft_scan+10,y_left+5), buf, font = font , fill = (0))

            buf = '  link number %d  ' % (w-1)
            buf2 = str(chain_name) + buf
            #buf = ('link number %d  '+chain_name %) (w-1)
            #print (buf)
            #draw.text((100,10), buf, fill = (255))
            ImageDraw.Draw(r).text((10,10), buf2, font = font , fill = (255))

            now = datetime.datetime.now()
            buf = (now.strftime("%Y-%m-%d %H:%M:%S"))
            #print (buf)
            #draw.text((100,20), buf, fill = (255))
            ImageDraw.Draw(r).text((10,35), buf, font = font , fill = (255))
            #draw.text((10, 10), "Hello World", font=font)
            #cv2.putText(draw, 'This one!', (100, 20), font, 0.8, (0, 255, 0), 2, cv2.LINE_AA)

            buf = ('Baseline File Name : '+BaseLine_File_Name)
            ImageDraw.Draw(r).text((10,60), buf, font = font , fill = (255))
            
            millisec1 = int(round(time.time() * 1000)) 
            print ("done1",(millisec1 - millisec))


            crap = baseline_data[w-1]
            this_baseline_len = float(crap)
            buf = "Baseline Link Length % 1.3fin" % (this_baseline_len)
            ImageDraw.Draw(r).text((10,85), buf, font = font , fill = (255))

            stretch_this_link = length_in - this_baseline_len
            buf = "Link Stretch : % 1.3fin" % (stretch_this_link)
            #buf2 = buf + str(stretch_limit)

            ImageDraw.Draw(r).text((10,110), buf, font = font , fill = (255))


            this_stretch_limit = float(stretch_limit)
            mark_this_link = "fasle"
            buf = "Alarm = False"

            if output_file_type == "absolute" :
                if length_in > this_stretch_limit :
                    buf = "Alarm = True"
                    mark_this_link = "true"
                    alarm_appender = "link %d     over size limit   length = %1.3f in\r" %((w-1),length_in)
                    alarm_list = alarm_list + alarm_appender

            else :   #delta
                if stretch_this_link > this_stretch_limit :
                    buf = "Alarm = True"
                    mark_this_link = "true"
                    alarm_appender = "link %d  over stretch limit   stretch = %1.3f in\r" %((w-1),stretch_this_link)
                    alarm_list = alarm_list + alarm_appender

            ImageDraw.Draw(r).text((10,135), buf, font = font , fill = (255))


            r.save(post_process_FN)

            #last_w = w

            if output_file_type == "absolute" :
                buf1 = "%1.3f\r\n" % (length_in)
                if (sequence!=0):
                    fcsv.write(buf1)
                    file_rec_count = file_rec_count+1

            if output_file_type == "delta" :
                buf1 = "%1.3f\r\n" % (stretch_this_link)
                if (sequence!=0):
                    fcsv.write(buf1)
                    file_rec_count = file_rec_count+1

            #imagex = cv2.imread(post_process_FN,0)
            #cv2.imshow('frame', imagex)
            #cv2.waitKey(1000)

            millisec1 = int(round(time.time() * 1000)) 
            print ("done2",(millisec1 - millisec))
            ser.write(bytes("!\r",'UTF-8'))
            if mark_this_link == "true" :
                ser.write(bytes("link processed ALARM\r",'UTF-8'))
            else:
                ser.write(bytes(" link processed OK  \r",'UTF-8'))

            if mark_this_link == "true" :
                    if paint_enable == "yes" :
                        ser.write(bytes("xxx3\r",'UTF-8'))
            else:
                    if paint_enable == "yes" :
                        ser.write(bytes("yyy3\r",'UTF-8'))

# When everything done, release the capture
GPIO.output(18, GPIO.LOW)
GPIO.cleanup()
cap.release()
cv2.destroyAllWindows()
