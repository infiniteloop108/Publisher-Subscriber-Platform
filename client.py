import sys
import socket

if len(sys.argv) != 4:
	print 'Usage python client.py name server_ip server_host'
	sys.exit(0)

HOST = sys.argv[2]
PORT = int(sys.argv[3])
name = sys.argv[1]

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
s.send('reg '+name)
resp = s.recv(1024)
if resp != 'Successfully Registered':
	print 'try'
