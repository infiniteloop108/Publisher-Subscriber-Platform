from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase
import datetime

db = SqliteExtDatabase('my_database.db')

class BaseModel(Model):
	class Meta:
		database = db

class User(BaseModel):
	username = CharField(unique=True)
	ip = CharField()

db.connect()
print 'Database Connected'

#Put if __main__ here
def db_reset():
	db.create_tables([User])
