from flask import g, session
import pymysql
import redis
import random
import string
import json
from exceptions.userException import *


class User():    

    __changed = {}
    _values = {}

    def __init__(self):
        raise NotInitializeable("User")

    def _init(self):
        """User Object"""
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user='laba', password='brUQJD1sAYeQaeuJ', db='laba', cursorclass=pymysql.cursors.DictCursor, host="localhost")
        self.cursor = g.db.cursor()
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host='localhost', port=6379, db=0)


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
    
    #def chkInitialized(self):
    #    if not hasattr(self, '_value'):
    #        print(dir (self))
    #        #raise UserNotInitialized()
    #    return f

    #@chkInitialized
    @property
    def id(self):
        return self._values["id"]
    
    @property
    def uuid(self):
        return self.__uuid
    
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
        return self.__firstName
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
            print("updated")
    
    def __serialize(self):
        self._values['atime'] = str(self._values['atime']) #Keep private! It's changing self.__value!!!
        self._values['ctime'] = str(self._values['ctime'])
        return json.dumps(self._values)
    
    def commit2redis(self):        
        g.redis.set(self._uuid, self.__serialize(), 300)

    def __del__(self):
        self.commit2db()
        self.cursor.close()
        g.db.commit()
        self.commit2redis()

class LoginUser(User):
    def __init__(self, username, passwd):
        """Checks User cred and logs in + moves to redis if ready"""
        User._init(self)
        self._values = self.queryOne("""SELECT
                id, username, firstName, lastName, email, ctime, atime, status, icon, enabled
                FROM users
                WHERE
                (username = %s or email = %s)
                AND
                password = SHA2(%s, 256)""", (username, username, passwd))
        if not self._values:
            raise BadUserCredentials(username)
        
        if not self._values["enabled"]:
            raise UserDisabled(username)
        
        self._uuid = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])
        session['uuid'] = self._uuid

class RedisUser(User):
    def __init__(self):
        User._init(self)
        self._uuid = session["uuid"]
        self._values = json.loads(g.redis.get(session['uuid']))
 
