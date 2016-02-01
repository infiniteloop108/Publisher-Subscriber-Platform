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

db.connect()
print 'Database Connected'

if __name__ == "__main__":
	if len(sys.argv) >=2 and sys.argv[1] == 'clear':
		db.close()
		os.remove('my_database.db')
		db.connect()
		db.create_tables([User])
		db.close()
		print 'Database cleared'
