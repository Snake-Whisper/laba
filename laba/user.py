from flask import g, session
import pymysql
import redis
import random
import string
import json
from exceptions.userException import BadUserCredentials, UserDisabled


class LoginUser():    

    def __init__(self, username, passwd, register=False):
        """User Object"""
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user='laba', password='brUQJD1sAYeQaeuJ', db='laba', cursorclass=pymysql.cursors.DictCursor, host="localhost")
        self.cursor = g.db.cursor()
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host='localhost', port=6379, db=0)
        #chkCred
        self.__values = self.queryOne("""SELECT
                id, username, firstName, lastName, email, ctime, atime, status, icon, enabled
                FROM users
                WHERE
                (username = %s or email = %s)
                AND
                password = SHA2(%s, 256)""", (username, username, passwd))
        if not self.__values:
            raise BadUserCredentials(username)
        
        if not self.__values["enabled"]:
            raise UserDisabled(username)

        self.__changed = {}

        #self.__id = self.values["id"]
        #self.__username = self.values["username"]
        #self.__firstName = self.values["firstName"]
        #self.__lastName = self.values["lastName"]
        #self.__email = self.values["email"]
        #self.__ctime = self.values["ctime"]
        #self.__atime = self.values["atime"] #last seen
        #self.__status = self.values["status"]
        #self.__icon = self.values["icon"]
        self.__uuid = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(32)])

        session['uuid'] = self.__uuid

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

    @property
    def id(self):
        return self.__values["id"]
    
    @property
    def uuid(self):
        return self.__uuid
    
    @property
    def username(self):
        return self.__values["username"]
    @username.setter
    def username(self, value):
        if self.__values["username"] != value:
            self.__values["username"] = value
            self.__changed['username'] = value

    @property
    def firstName(self):
        return self.__firstName
    @firstName.setter
    def firstName(self, value):
        if self.__values["firstName"] != value:
            self.__values["firstName"] = value
            self.__changed['firstName'] = value

    @property
    def lastName(self):
        return self.__values["lastName"]
    @lastName.setter
    def lastName(self, value):
        if self.__values["lastName"] != value:
            self.__values["lastName"] = value
            self.__changed['lastName'] = value

    @property
    def email(self):
        return self.__values["email"]
    @email.setter
    def email(self, value):
        if self.__values["email"] != value:
            self.__values["email"] = value
            self.__changed['email'] = value

    @property
    def ctime(self):
        return self.__values["ctime"]
    @ctime.setter
    def ctime(self, value):
        if self.__values["ctime"] != value:
            self.__values["ctime"] = value
            self.__changed['ctime'] = value
    
    @property
    def atime(self):
        return self.__values["atime"]
    @atime.setter
    def atime(self, value):
        if self.__values["atime"] != value:
            self.__values["atime"] = value
            self.__changed['atime'] = value

    @property
    def status(self):
        return self.__values["status"]
    @status.setter
    def status(self, value):
        if self.__values["status"] != value:
            self.__values["status"] = value
            self.__changed['status'] = value

    @property
    def icon(self):
        return self.__values["icon"]
    @icon.setter
    def icon(self, value):
        if self.__values["icon"] != value:
            self.__values["icon"] = value
            self.__changed['icon'] = value
    
    def changePwd (self, old, new):
        r = self.cursor.execute("UPDATE users SET password=SHA2(%s, 256) WHERE id=%s AND password=SHA2(%s, 256);", (new, self.__id, old))
        if not r:
            raise BadUserCredentials(self.__username)
    
    def commit2db(self):
        if self.__changed:
            sql="UPDATE users SET {0} WHERE users.id = {1}".format(", ".join(i+"=%s" for i in self.__changed.keys()), self.__values["id"])
            self.query(sql, tuple(self.__changed.values()))
            print("updated")
    
    def __serialize(self):
        self.__values['atime'] = str(self.__values['atime']) #Keep private! It's changing self.__value!!!
        self.__values['ctime'] = str(self.__values['ctime'])
        return json.dumps(self.__values)
    
    def commit2redis(self):        
        g.redis.set(self.__uuid, self.__serialize(), 60)

    def __del__(self):
        self.commit2db()
        self.cursor.close()
        g.db.commit()
        self.commit2redis()
        