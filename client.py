import sys
import socket
from thread import *

if len(sys.argv) != 4:
	print '\033[91m' + 'Usage python client.py username server_ip server_port' + '\033[0m'
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
		print '\033[91m' + 'Use the client from the IP you registered' + '\033[0m'
		s.close()
		sys.exit(0)
s.close()

def process_message(text):
	print '\n--------------------'
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
	if resp != '':
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
	ch = raw_input('Enter Channel Name: ')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send('pub '+name+' '+ch)
	resp = s.recv(1024)
	s.close()
	print 'Enter message (max 2000 chars, end by EOF (Ctrl+D)'
	message = sys.stdin.readlines()
	req = 'publish ' + name + ' ' + ch + ' '
	for q in message:
		req = req + q
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send(req.rstrip())
	resp = s.recv(1024)
	s.close()
	if resp == 'Published!':
		print '\033[92m' + resp + '\033[0m'
	else:
		print '\033[91m' + resp + '\033[0m'

def subscribe():
	ch = raw_input('Enter Channel Name: ')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send('sub '+name+' '+ch)
	resp = s.recv(1024)
	s.close()
	if resp == 'Subscription added':
		print '\033[92m' + resp + '\033[0m'
	else:
		print '\033[91m' + resp + '\033[0m'

def unsubscribe():
	ch = raw_input('Enter Channel Name: ')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send('unsub '+name+' '+ch)
	resp = s.recv(1024)
	s.close()
	if resp == 'Subscription removed':
		print '\033[92m' + resp + '\033[0m'
	else:
		print '\033[91m' + resp + '\033[0m'

def change():
	ch = raw_input('Enter New IP: ')
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((HOST, PORT))
	s.send('ch '+name+' '+ch)
	resp = s.recv(1024)
	s.close()
	if resp == 'IP changed':
		print '\033[92m' + resp + '\033[0m'
		print 'Now login from new IP'
		print '\033[94m' + 'Goodbye!' + '\033[0m'
		sys.exit(0)
	else:
		print '\033[91m' + resp + '\033[0m'

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
