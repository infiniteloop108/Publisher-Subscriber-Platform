import socket
import signal
import sys
from database import *
from thread import *

HOST = 'localhost'
PORT = 6042

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ', Error : ' + msg[1]
	sys.exit()

print 'Socket bind complete'
s.listen(10)
print 'Socket listening on ' + HOST + ':' + str(PORT)

def quitting_server(signal, frame):
	print 'Closing the server'
	s.close()
	sys.exit(0)

signal.signal(signal.SIGINT, quitting_server)

def check_id(name):
	l = len(name)
	if l == 0:
		return 0
	for i in range(l):
		if name[i] < 'a' or name[i] > 'z':
			return 0
	return 1

def match_ip(name, ip):
	return 1

def process_request(req, addr):
	#Can be reg name, poll name, pub name ch_id, sub name ch_id
	#publish name ch_id message(1024)
	#Check request format
	#Check ids lowercase
	#Match IP
	#Return parsed request
	ind = req.find(' ')
	if ind == -1:
		return 'Invalid Format'
	r = req[:ind]
	req = req[ind+1:]
	name = ''
	ch_id = ''
	text = ''
	if r != "reg" and r!="poll" and r!="pub" and r!="sub" and r!= "publish":
		return 'Invalid request'
	
	if r == "reg" or r == "poll":
		name = req
	else:
		ind = req.find(' ')
		if ind == -1:
			return 'Wrong Format'
		name = req[:ind]
		req = req[ind+1:]
		ch_id = req
		if r == "publish":
			ind = req.find(' ')
			if ind == -1:
				return 'Wrong Format'
			ch_id = req[:ind]
			text = req[ind+1:]
		if check_id(ch_id)==0:
			return 'Channel ID should have small letters only'
	
	if check_id(name) == 0:
		return 'Name should have small letters only'
	

	return ''

def client_thread(conn, addr):
	conn.send('Welcome to Pub/Sub\n')
	req = conn.recv(2048)
	req = req.rstrip()
	print 'Request ' + req + ' from ' + addr[0]
	err = process_request(req, addr)
	if err == '' :
		print 'Request ' + req + ' processed'
	else:
		print 'Error in request: ' + req + ', Error: ' + err
		conn.sendall('Error: ' + err)
		conn.close()

while 1:
	conn, addr = s.accept()
	print 'Connected with '  + addr[0] + ':' + str(addr[1])
	start_new_thread(client_thread, (conn,addr))

s.close()
