#!/usr/bin/python3
import socket
import time
import json
import RPi.GPIO as gpio
#from gpiozero import LED

#must be modified===
DEVICEID='1051809***'
APIKEY='c69aea06510***'
#modify end=========
#led = LED(17)
host="www.bigiot.net"
port=8181

#connect bigiot
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.settimeout(0)
while True:
	try:
		s.connect((host,port))
		break
	except:
		print('waiting for connect bigiot.net...')
		time.sleep(2)

#check in bigiot
checkinBytes=bytes('{\"M\":\"checkin\",\"ID\":\"'+DEVICEID+'\",\"K\":\"'+APIKEY+'\"}\n',encoding='utf8')
s.sendall(checkinBytes)

#keep online with bigiot function
data=b''
flag=1
t=time.time()
def keepOnline(t):
	if time.time()-t>40:
		s.sendall(b'{\"M\":\"status\"}\n')
		print('check status')
		return time.time()
	else:
		return t

#say something to other device function
def say(s,id,content):
	sayBytes=bytes('{\"M\":\"say\",\"ID\":\"'+id+'\",\"C\":\"'+content+'\"}\n',encoding='utf8')
	s.sendall(sayBytes)

#deal with message coming in
def process(msg,s,checkinBytes):
	msg=json.loads(msg)
	if msg['M'] == 'connected':
		s.sendall(checkinBytes)
	if msg['M'] == 'login':
		say(s,msg['ID'],'Welcome! Your public ID is '+msg['ID'])
	if msg['M'] == 'say':
		say(s,msg['ID'],'You have send to me:{'+msg['C']+'}')
		'''
		if msg['C'] == "play":
			led.on()
			say(s,msg['ID'],'LED turns on!')
		if msg['C'] == "stop":
			led.off()
			say(s,msg['ID'],'LED turns off!')
		'''
		if msg['C']=="rest":
			gpiocontrol(2)
			print('rest')
			say(s,msg['ID'],'rest')
		if msg['C']=="fast":
			gpiocontrol(3)
			print('fastmod')
			say(s,msg['ID'],'fastmod')
		if msg['C']=="study":
			gpiocontrol(4)
			print('study')
			say(s,msg['ID'],'step-forward')
	#for key in msg:
	#	print(key,msg[key])
	#print('msg',type(msg))
gpio.setmode(gpio.BCM)
gpio.setup(2,gpio.OUT)
gpio.setup(3,gpio.OUT)
gpio.setup(4,gpio.OUT)

def gpiocontrol(pin):
	gpio.output(pin,gpio.HIGH)
	time.sleep(1)
	gpio.output(pin,gpio.LOW)
#main while
while True:
	try:
		d=s.recv(1)
		flag=True
	except:
		flag=False
		time.sleep(1)
		t = keepOnline(t)
	if flag:
		if d!=b'\n':
			data+=d
		else:
			msg=str(data,encoding='utf-8')
			process(msg,s,checkinBytes)
			print(msg)
			data=b''
