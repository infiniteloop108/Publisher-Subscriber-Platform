import socket
import signal
import sys
from database import *
from thread import *

if len(sys.argv) != 3:
	print 'Usage python server.py IP PORT'
	sys.exit(0)

HOST = sys.argv[1]
PORT = int(sys.argv[2])

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
	print 'Closing the server (socket and database)'
	s.close()
	db.close()
	sys.exit(0)

signal.signal(signal.SIGINT, quitting_server)


def check_id(name):
	l = len(name)
	if l == 0:
		return 0
	for i in range(l):
		if (not ((name[i] >= 'a' and name[i] <= 'z') or (name[i] >= '0' and name[i] <= '9'))):
			return 0
	return 1

user_socket = {}

def update_user(name):
	#Look at all the subscriptions of user with username=name
	#If any subscription is behind, send it
	if name in user_socket:
		conn = user_socket[name]
		u = User.get(User.username == name)
		for subscription in ChannelSubscriber.select().where(ChannelSubscriber.sub_id == u):
			c = subscription.ch_id
			ts = subscription.ts
			if c.num > ts:
				#Send feed with sid = ts
				f = Feed.get(Feed.ch_id == c, Feed.sid == ts)
				try:
					conn.sendall('Channel:'+c.name+'\nPublisher:'+f.pub_id.username+'\ntext:'+f.text+'\n')
					resp = conn.recv(1024)
					resp = resp.rstrip()
					if(resp == 'Success'):
						subscription.ts = subscription.ts+1
						subscription.save()
						conn.close()
						user_socket.pop(name, None)
						return 1
					else:
						conn.close()
						user_socket.pop(name, None)
						return 2
				except socket.error, e:
					user_socket.pop(name, None)
					return 2
	return 0

def process_request(req, ip):
	#Can be reg name, poll name, pub name ch_id, sub name ch_id
	#unsub name ch_id, publish name ch_id message(1024), ch name ip
	ind = req.find(' ')
	if ind == -1:
		return 'Invalid Format'
	r = req[:ind]
	req = req[ind+1:]
	name = ''
	ch_id = ''
	new_ip = ''
	text = ''
	if r!= "ch" and r != "reg" and r!="poll" and r!="pub" and r!="sub" and r!= "publish" and r!="unsub":
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
		new_ip = req
		if r == "publish":
			ind = req.find(' ')
			if ind == -1:
				return 'Wrong Format'
			ch_id = req[:ind]
			text = req[ind+1:]
		if r != 'ch':
			if check_id(ch_id)==0:
				return 'Channel name should have small letters/numbers only'

	if check_id(name) == 0:
		return 'Username should have small letters/numbers only'

	if r == 'reg':
		#Check if user already exists
		try:
			u = User.get(User.username == name)
			return 'User already exists'
		except User.DoesNotExist:
			u = User.create(username = name, ip = ip)
			conn.sendall('Successfully Registered')
			conn.close()
			return ''

	try:
		u = User.get(User.username == name)
		if u.ip != ip:
			return 'Access the system from the IP you registered'
		if r == 'pub':
			try:
				c = Channel.get(Channel.name == ch_id)
			except Channel.DoesNotExist:
				#Create a new channel
				Channel.create(name = ch_id)
				c = Channel.get(Channel.name == ch_id)
			finally:
				try:
					publisher = ChannelPublisher.get(ChannelPublisher.ch_id == c, ChannelPublisher.pub_id == u)
					return 'Already publishing'
				except ChannelPublisher.DoesNotExist:
					ChannelPublisher.create(ch_id = c, pub_id = u)
					conn.sendall('Publisher added')
					conn.close()
		elif r == 'sub':
			try:
				c = Channel.get(Channel.name == ch_id)
				try:
					subscription = ChannelSubscriber.get(ChannelSubscriber.ch_id == c, ChannelSubscriber.sub_id == u)
					return 'User already subscribed'
				except ChannelSubscriber.DoesNotExist:
					#Add this user as a subscriber
					ChannelSubscriber.create(ch_id = c, sub_id = u, ts = c.num)
					conn.sendall('Subscription added')
					conn.close()
			except Channel.DoesNotExist:
				return 'Channel does not exist'
		elif r == 'ch':
			u.ip = new_ip
			u.save()
			conn.sendall('IP changed')
			conn.close()
		elif r == 'unsub':
			try:
				c = Channel.get(Channel.name == ch_id)
				try:
					subscription = ChannelSubscriber.get(ChannelSubscriber.ch_id == c, ChannelSubscriber.sub_id == u)
					subscription.delete_instance()
					conn.sendall('Subscription removed')
					conn.close()
				except ChannelSubscriber.DoesNotExist:
					return 'User not subscribed'
			except Channel.DoesNotExist:
				return 'Channel does not exist'
		elif r == 'publish':
			try:
				c = Channel.get(Channel.name == ch_id)
				try:
					publisher = ChannelPublisher.get(ChannelPublisher.ch_id == c, ChannelPublisher.pub_id == u)
					Feed.create(ch_id = c, pub_id = u, text = text, sid = c.num)
					c.num = c.num+1
					c.save()
					conn.sendall('Published!')
					for subscriber in ChannelSubscriber.select().where(ChannelSubscriber.ch_id == c):
						update_user(subscriber.sub_id.username)
					conn.close()
				except ChannelPublisher.DoesNotExist:
					return 'User cannot publish to this channel'
					conn.sendall('Publisher added')
					conn.close()
			except Channel.DoesNotExist:
				return 'Channel does not exist'
		elif r == 'poll':
			user_socket[name] = conn
			update_user(name)
	except User.DoesNotExist:
		return 'Username does not exist'
	return ''

def client_thread(conn, addr):
	req = conn.recv(2048)
	req = req.rstrip()
	print 'Request ' + req + ' from ' + addr[0]
	err = process_request(req, addr[0])
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
