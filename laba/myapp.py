from flask import Flask, render_template, g
import pymysql
from user import LoginUser

app = Flask(__name__)

app.config.update(
    SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0",
	AUTO_LOGOUT = 43200,
	MAX_CONTENT_LENGTH = 30 * 1024 * 1024,
	DATADIR = "static/files"
)

def getRedis():
	if not hasattr(g, 'redis'):
		g.redis = FlaskRedis(app)
	return g.redis

def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user='laba', password='brUQJD1sAYeQaeuJ', db='laba', cursorclass=pymysql.cursors.DictCursor, host="localhost")
	return g.db.cursor()

@app.route("/")
def test():
	u = LoginUser("user1", "pwd1!")
	u.email = "test@ruschinski.ml"
	u.firstName = "jack"
	u.lastName = "sparrow"
	print (u.uuid)
	v = getRedis()
	return "hallo"

@app.teardown_appcontext
def closeDB(error):
	if hasattr(g, 'db'):
		g.db.commit()
		g.db.close()

@app.cli.command('initDB')
def initdb():
	with app.open_resource('schema.sql', mode='r') as f:
		c = getDBCursor()
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close() 
		c.close()
		g.db.commit() #manual tear down!

@app.cli.command('randFill')
def randomFill():
	with app.open_resource('testdata.sql', mode='r') as f:
		c = getDBCursor()
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close() 
		c.close()
		g.db.commit() #manual tear down!

