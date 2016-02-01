import socket
import signal
import sys
from thread import *

HOST = 'localhost'
PORT = 6042

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
	s.bind((HOST, PORT))
except socket.error , msg:
	print 'Bind failed. Error Code : ' + str(msg[0]) + ' Error : ' + msg[1]
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
	return 1

def match_ip(name, ip):
	return 1

def check_request(req, addr):
	#Can be register name, poll name, pub name ch_id, sub name ch_id
	#Check request format
	#Check ids lowercase
	#Match IP
	#Return parsed request
	return 1

def client_thread(conn, addr):
	conn.send('Welcome to Pub/Sub\n')
	request = conn.recv(1024)
	print 'Request ' + request + ' from ' + addr[0]

while 1:
	conn, addr = s.accept()
	print 'Connected with '  + addr[0] + ':' + str(addr[1])
	start_new_thread(client_thread, (conn,addr))

s.close()
