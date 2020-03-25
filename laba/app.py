from flask import Flask, render_template, g, redirect, request, flash
import pymysql
import redis
from user import *
from functools import wraps
from validate_email import validate_email


app = Flask(__name__)

app.config.update(
    SECRET_KEY = '\x81H\xb8\xa3S\xf8\x8b\xbd"o\xca\xd7\x08\xa4op\x07\xb5\xde\x87\xb8\xcc\xe8\x86\\\xffS\xea8\x86"\x97',
	REDIS_URL = "redis://localhost:6379/0",
	AUTO_LOGOUT = 43200,
	TOKEN_TIMEOUT = 60,
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

def login_required(f):
	@wraps(f)
	def dec_funct(*args, **kwargs):
		try:
			if not hasattr (g, 'user'):
				g.user = RedisUser(app)
		except UserNotInitialized:
			print("raus")
			return redirect("/login")
		return f(*args, **kwargs)
	return dec_funct


@app.route("/login", methods=["GET", "POST"])
def login():
	try:
		g.user = RedisUser(app)
		return redirect('/')
	except UserNotInitialized:
		if request.method == 'POST':
			if all([request.form['username'], request.form['password']]):
				try:
					g.user = LoginUser(app, request.form['username'], request.form['password'])
					return redirect("/")
				except BadUserCredentials:
					flash("authentication failure")
					return redirect("/login")			
		return render_template("login.html")

@app.route("/logout")
@login_required #ironic
def logOut():
	g.user.logOut()
	return redirect("/login")

@app.route("/register", methods=["GET", "POST"])
def register():
	if request.method == "POST":
		if not all([request.form["username"],
				request.form["password"],
				request.form["Confpassword"],
				request.form["firstName"],
				request.form["lastName"],
				request.form["email"]]):
			flash("Fill all fields")
			return redirect ("/register")
		if request.form["password"] != request.form["Confpassword"]:
			flash("Please check your password")
			return redirect("/register")
		if not validate_email(request.form["email"]):
			flash("Please check your email address")
			return redirect("/register")
			
		u = RegisterUser(app)
		try:
			u.username = request.form["username"]
			u.email = request.form["email"]
		except RegistrationErrorDupplicate as e:
			flash(str(e))
			return redirect("/register")
		u.firstName = request.form["firstName"]
		u.lastName = request.form["lastName"]
		u.password = request.form["password"]

		token = u.commit2redis()

		#TODO: Add Mail transport!!!

		#   _______    
		#  |==   []| 
		#  |  ==== |
		#//'-------'
		#
		return redirect("/confirm/AccountRegistration/" + token)

	return render_template("register.html")

@app.route("/")
@login_required
def root():
	return "hallo"

@app.route("/confirm/AccountRegistration/<token>")
def confirmAccountRegistration(token):
	u = RegisterUser(app)
	try:
		u.confirmToken(token)
		return redirect("/login") #add friendly token page?
	except InvalidToken:
		return "Token invalid"

@app.teardown_appcontext
def closeDB(error):
	if hasattr(g, 'user'):
		del g.user #exec destruct before app context breaks down
	if hasattr(g, 'db'):
		g.db.commit()
		g.db.close()



#   __    __    
#   \ \   \ \   
#    \ \   \ \  
#    / /   / /  
#   /_/   /_/   
#             

def getRedis():
	if not hasattr(g, 'redis'):
		g.redis = redis.Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
	return g.redis

def getDBCursor():
	if not hasattr(g, 'db'):
		g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
	return g.db.cursor()

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