from flask import Flask, render_template, g
import pymysql
import redis
from user import *

app = Flask(__name__)

app.config.update(
    SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0",
	AUTO_LOGOUT = 43200,
	MAX_CONTENT_LENGTH = 30 * 1024 * 1024,
	DATADIR = "static/files",
	DB_USER = "laba",
	DB_DB = "laba",
	DB_PWD = "brUQJD1sAYeQaeuJ",
	DB_HOST = "localhost",
	REDIS_HOST = "localhost",
	REDIS_DB = 0,
	REDIS_PORT = 6379
)

def getRedis():
	if not hasattr(g, 'redis'):
		g.redis = redis.Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
	return g.redis

def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
	return g.db.cursor()


@app.route("/")
def test():
	u = LoginUser(app, "user1", "pwd1!")
	u.logOut()
	#u = RedisUser()
	#u = User()
	#u = LoginUser()
	#u.email = "test@ruschinski.ml"
	#u.firstName = "jack"
	#u.lastName = "sparrow"
	#print (u.uuid)
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

@app.cli.command('reset')
def reset():
	c = getDBCursor()
	with app.open_resource('schema.sql', mode='r') as f:
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close()
	with app.open_resource('testdata.sql', mode='r') as f:
		for query in f.read().split(";")[:-1]:
			print(query)
			c.execute(query)
		f.close() 
	c.close()
	g.db.commit()

if __name__ == "__main__":
	app.run(debug=True)