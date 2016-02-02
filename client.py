import sys
import socket
from thread import *

if len(sys.argv) != 4:
	print 'Usage python client.py username server_ip server_port'
	sys.exit(0)

HOST = sys.argv[2]
PORT = int(sys.argv[3])
name = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('reg '+name)
resp = s.recv(1024)
s.close()
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
if resp != 'Successfully Registered':
	s.send('pub '+name+' trych')
	resp = s.recv(1024)
	if 'IP' in resp:
		print 'Use the client from the IP you registered'
		s.close()
		sys.exit(0)
s.close()

def process_message(text):
	print '--------------------'
	print '\033[94m' + 'You have an update!' + '\033[0m'
	print '--------------------'
	print text
	print '--------------------'

def long_polling():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((HOST, PORT))
	sock.send('poll ' + name)
	resp = sock.recv(2048)
	sock.send('Success')
	sock.close()
	process_message(resp)
	long_polling()

start_new_thread(long_polling, ())

print '\033[95m' + 'Welcome to Pub/Sub Platform' + '\033[0m'
print 'You are logged in as ' + '\033[92m' + name + '\033[0m'

def print_help():
	print '--------------------------------'
	print 'Following commands are available'
	print '--------------------------------'
	print 'publish(p)'
	print 'subscribe(s)'
	print 'unsububscribe(u)'
	print 'change(c)'
	print 'help(h)'
	print 'quit(q)'
	print '--------------------------------'

print_help()

def publish():
	a=1

def subscribe():
	a=1

def unsubscribe():
	a=1

def change():
	a=1

while 1:
	cmd = raw_input('Enter Command: ')
	if cmd == 'p' or cmd == 'publish':
		publish()
	elif cmd == 's' or cmd == 'subscribe':
		subscribe()
	elif cmd == 'u' or cmd == 'unsubscribe':
		unsubscribe()
	elif cmd == 'c' or cmd == 'change':
		change()
	elif cmd == 'h' or cmd == 'help':
		print_help()
	elif cmd == 'q' or cmd == 'quit':
		print '\033[94m' + 'Goodbye!' + '\033[0m'
		sys.exit(0)
	else:
		print '\033[91m' + 'Invalid Command' + '\033[0m'
		print_help()
