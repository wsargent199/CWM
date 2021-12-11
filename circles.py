from zipfile import ZipFile
from os import path
from os.path import basename
from scipy.spatial import distance as dist
#from imutils import perspective
#from imutils import contours

fromaddr = "cwm.sn.1021@gmail.com"
toaddr = "sargentw@gmail.com"
password = "digilube1021"
chain_name = "chainxxx"


import numpy as np
import cv2
import socket
import urllib.request

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

msg = MIMEMultipart()
msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = chain_name


body = "Chain_Name: "
buf = chain_name
body = body + buf




msg.attach(MIMEText(body, 'plain'))

filename = "/home/pi/CWM_DATA/cfg.txt"
attachment = open("/home/pi/CWM_DATA/cfg.txt", "rb")
part = MIMEBase('application', 'octet-stream')
part.set_payload((attachment).read())
encoders.encode_base64(part)
part.add_header('Content-Disposition', "attachment; filename= %s" % filename)
msg.attach(part)


server = smtplib.SMTP('smtp.gmail.com', 587)
server.starttls()
server.login(fromaddr, "digilube1021")
text = msg.as_string()
server.sendmail(fromaddr, toaddr, text)
server.quit()
