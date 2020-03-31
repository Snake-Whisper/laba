from flask import g, session
import pymysql
import redis
import random
import string
from json import loads, dumps
from exceptions.userException import *
from hashlib import sha256


class User():    

    __changed = {}
    _values = {}
    __loggedIn = True
    __initialized = False
    __health = False

    def __init__(self):
        raise NotInitializeable("User")

    def _init(self, app):
        """User Object"""
        self.app = app
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
        self.__initialized = True


#      |\_/|                  
#      | @ @   Watch! 
#      |   <>              _  
#      |  _/\------____ ((| |))
#      |               `--' |   
#  ____|_       ___|   |___.' 
# /_/_____/____/_______|
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    def query(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchall()
    
    def queryOne(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchone()
    
    def recover(self):
        """Call to prevent pymysql Interface error after recovering from session cache"""
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=self.app.config["DB_USER"], db=self.app.config["DB_DB"], password=self.app.config["DB_PWD"], host=self.app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host=self.app.config["REDIS_HOST"], port=self.app.config["REDIS_PORT"], db=self.app.config["REDIS_DB"])
    
    @property
    def wsuuid(self):
        return g.redis.get(self._values["username"])
    
    @wsuuid.setter
    def wsuuid(self, wsuuid):
        g.redis.set(self._values["username"], wsuuid, self.app.config["AUTO_LOGOUT"])

    @property
    def id(self):
        return self._values["id"]
    
    @property
    def uuid(self):
        return self.__uuid

    @property
    def health(self):
        return self.__health
    
    @property
    def username(self):
        return self._values["username"]
    @username.setter
    def username(self, value):
        if self._values["username"] != value:
            self._values["username"] = value
            self.__changed['username'] = value

    @property
    def firstName(self):
        return self._values["firstName"]
    @firstName.setter
    def firstName(self, value):
        if self._values["firstName"] != value:
            self._values["firstName"] = value
            self.__changed['firstName'] = value

    @property
    def lastName(self):
        return self._values["lastName"]
    @lastName.setter
    def lastName(self, value):
        if self._values["lastName"] != value:
            self._values["lastName"] = value
            self.__changed['lastName'] = value

    @property
    def email(self):
        return self._values["email"]
    @email.setter
    def email(self, value):
        if self._values["email"] != value:
            self._values["email"] = value
            self.__changed['email'] = value

    @property
    def ctime(self):
        return self._values["ctime"]
    @ctime.setter
    def ctime(self, value):
        if self._values["ctime"] != value:
            self._values["ctime"] = value
            self.__changed['ctime'] = value
    
    @property
    def atime(self):
        return self._values["atime"]
    @atime.setter
    def atime(self, value):
        if self._values["atime"] != value:
            self._values["atime"] = value
            self.__changed['atime'] = value

    @property
    def status(self):
        return self._values["status"]
    @status.setter
    def status(self, value):
        if self._values["status"] != value:
            self._values["status"] = value
            self.__changed['status'] = value

    @property
    def icon(self):
        return self._values["icon"]
    @icon.setter
    def icon(self, value):
        if self._values["icon"] != value:
            self._values["icon"] = value
            self.__changed['icon'] = value
    
    def changePwd (self, old, new):
        r = self.cursor.execute("UPDATE users SET password=SHA2(%s, 256) WHERE id=%s AND password=SHA2(%s, 256);", (new, self.__id, old))
        if not r:
            raise BadUserCredentials(self.__username)
    
    def commit2db(self):
        if self.__changed:
            sql="UPDATE users SET {0} WHERE users.id = {1}".format(", ".join(i+"=%s" for i in self.__changed.keys()), self._values["id"])
            self.query(sql, tuple(self.__changed.values()))
    
    def __serialize(self):
        self._values['atime'] = str(self._values['atime']) #Keep private! It's changing self.__value!!!
        self._values['ctime'] = str(self._values['ctime'])
        return dumps(self._values)
    
    def commit2redis(self):
        g.redis.set(self._uuid, self.__serialize(), self.app.config["AUTO_LOGOUT"])
    
    def logOut(self):
        self.__loggedIn = False
        g.redis.delete(session["uuid"])
        session.pop("uuid")

    def startSession(self):
        self.__health = True

    def __del__(self):
        if self.__initialized and self.__health:
            self.commit2db()
            self.cursor.close()
            g.db.commit()
            if self.__loggedIn:
                self.commit2redis()

class LoginUser(User):
    def __init__(self, app, username, password):
        """Checks User cred and logs in + moves to redis if ready"""
        User._init(self, app)
        self._values = self.queryOne("""SELECT
                id, username, firstName, lastName, email, ctime, atime, status, icon, enabled
                FROM users
                WHERE
                (username = %s or email = %s)
                AND
                password = SHA2(%s, 256)""", (username, username, password))

        if not self._values:
            raise BadUserCredentials(username)
        
        if not self._values["enabled"]:
            raise UserDisabled(username)
        
        self.startSession()
        self._uuid = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        session['uuid'] = self._uuid

class RedisUser(User):
    def __init__(self, app):
        if not 'uuid' in session:
            raise UserNotInitialized()
        User._init(self, app)
        self._uuid = session["uuid"]
        vals = g.redis.get(session['uuid'])
        if not vals:
            session.pop("uuid")
            raise UserNotInitialized()
        self.startSession()
        self._values = loads(vals)
 
class RegisterUser():
    _values = {}
    def __init__(self, app):
        self.app = app
        assert not 'uuid' in session
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
    
    def query(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchall()
    
    def queryOne(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchone()

    @property
    def username(self):
        return self._values["username"]
    @username.setter
    def username(self, value):
        if self.queryOne("SELECT id FROM users WHERE username=%s", value):
            raise RegistrationErrorDupplicate("username")
        self._values["username"] = value

    @property
    def email(self):
        return self._values["email"]
    @email.setter
    def email(self, value):
        if self.queryOne("SELECT id FROM users WHERE email=%s", value):
            raise RegistrationErrorDupplicate("email")
        self._values["email"] = value
    
    @property
    def firstName(self):
        return self._values["firstName"]
    @firstName.setter
    def firstName(self, value):        
        self._values["firstName"] = value
    
    @property
    def lastName(self):
        return self._values["lastName"]
    @lastName.setter
    def lastName(self, value):
        self._values["lastName"] = value
    @property
    def password(self):
        return self._values["password"]
    @password.setter
    def password(self, val):
        self._values["password"] = sha256(val.encode()).hexdigest()

    def commit2redis(self):
        if not all(k in self._values for k in ["email", "password", "username", "firstName", "lastName"]):
            for i in ["email", "password", "username", "firstName", "lastName"]:
                if i not in self._values:
                    raise RegistrationErrorInfoMissing(i)
        token = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        g.redis.set(token, dumps(self._values), self.app.config["TOKEN_TIMEOUT"])
        return token
    
    def confirmToken(self, token):
        vals = loads(g.redis.get(token))
        if not vals:
            raise InvalidToken(token)
        g.redis.delete(token)
        #WARNING: No check for dupl entry -> time from registerRequest to confirmation: unprotected ~ Problem?
        #Without Exception Handling in Prod. env.:  YES -> apk BBQ
        try:
            self.query("INSERT INTO users (email, password, username, firstname, lastname) VALUES (%s, %s, %s, %s, %s)", (
                vals["email"],
                vals["password"],
                vals["username"],
                vals["firstName"],
                vals["lastName"]))
        except pymysql.IntegrityError:
            raise RegistrationErrorDupplicate("email / username")
        
