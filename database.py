from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime
import sys, os

db = SqliteExtDatabase('my_database.db')

class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	username = CharField(unique=True)
	ip = CharField()

class Channel(BaseModel):
	name = CharField(unique=True)
	num = IntegerField(default=0)

class ChannelPublisher(BaseModel):
	ch_id = ForeignKeyField(Channel, related_name='channel_pub')
	pub_id = ForeignKeyField(User, related_name='publisher')

class ChannelSubscriber(BaseModel):
	ch_id = ForeignKeyField(Channel, related_name='channel_sub')
	sub_id = ForeignKeyField(User, related_name='subscriber')
	ts = IntegerField()

class Feed(BaseModel):
	ch_id = ForeignKeyField(Channel, related_name='channel_feed')
	pub_id = ForeignKeyField(User, related_name='publisher_feed')
	text = CharField()
	sid = IntegerField()

db.connect()
print 'Database Connected'

if __name__ == "__main__":
	if len(sys.argv) >=2 and sys.argv[1] == 'clear':
		db.close()
		os.remove('my_database.db')
		db.connect()
		db.create_tables([User, Channel, ChannelPublisher, ChannelSubscriber, Feed])
		db.close()
		print 'Database cleared'
