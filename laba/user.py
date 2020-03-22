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
        res = self.queryOne("""SELECT
                id, username, firstName, lastName, email, ctime, atime, status, icon, enabled
                FROM users
                WHERE
                (username = %s or email = %s)
                AND
                password = SHA2(%s, 256)""", (username, username, passwd))
        if not res:
            raise BadUserCredentials(username)
        
        if not res["enabled"]:
            raise UserDisabled(username)

        self.__changed = {}

        self.__id = res["id"]
        self.__username = res["username"]
        self.__firstName = res["firstName"]
        self.__lastName = res["lastName"]
        self.__email = res["email"]
        self.__ctime = res["ctime"]
        self.__atime = res["atime"] #last seen
        self.__status = res["status"]
        self.__icon = res["icon"]
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
        return self.__id
    
    @property
    def uuid(self):
        return self.__uuid
    
    @property
    def username(self):
        return self.__username
    @username.setter
    def username(self, value):
        if self.__username != value:
            self.__username = value
            self.__changed['username'] = value

    @property
    def firstName(self):
        return self.__firstName
    @firstName.setter
    def firstName(self, value):
        if self.__firstName != value:
            self.__firstName = value
            self.__changed['firstName'] = value

    @property
    def lastName(self):
        return self.__lastName
    @lastName.setter
    def lastName(self, value):
        if self.__lastName != value:
            self.__lastName = value
            self.__changed['lastName'] = value

    @property
    def email(self):
        return self.__email
    @email.setter
    def email(self, value):
        if self.__email != value:
            self.__email = value
            self.__changed['email'] = value

    @property
    def ctime(self):
        return self.__ctime
    @ctime.setter
    def ctime(self, value):
        if self.__ctime != value:
            self.__ctime = value
            self.__changed['ctime'] = value
    
    @property
    def atime(self):
        return self.__atime
    @atime.setter
    def atime(self, value):
        if self.__atime != value:
            self.__atime = value
            self.__changed['atime'] = value

    @property
    def status(self):
        return self.__status
    @status.setter
    def status(self, value):
        if self.__status != value:
            self.__status = value
            self.__changed['status'] = value

    @property
    def icon(self):
        return self.__icon
    @icon.setter
    def icon(self, value):
        if self.__icon != value:
            self.__icon = value
            self.__changed['icon'] = value
    
    def changePwd (self, old, new):
        r = self.cursor.execute("UPDATE users SET password=SHA2(%s, 256) WHERE id=%s AND password=SHA2(%s, 256);", (new, self.__id, old))
        if not r:
            raise BadUserCredentials(self.__username)
    
    def commit2db(self):
        if self.__changed:
            sql="UPDATE users SET {0} WHERE users.id = {1}".format(", ".join(i+"=%s" for i in self.__changed.keys()), self.__id)
            self.query(sql, tuple(self.__changed.values()))
    
    def commit2redis(self):
        vars = {"id" : self.__id,
        "username" : self.__username,
        "firstName" : self.__firstName,
        "lastName" : self.__lastName,
        "email" : self.__email,
        "ctime" : str(self.__ctime),
        "atime" : str(self.__atime),
        "status" : self.__status,
        "icon" : self.__icon}
        print (vars)
        g.redis.set(self.__uuid, json.dumps(vars))

    def __del__(self):
        self.commit2db()
        self.cursor.close()
        g.db.commit()
        self.commit2redis()
        