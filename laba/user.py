from flask import g
import pymysql
from exceptions.userException import BadUserCredentials, UserDisabled

class User():
    
    def query(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchall()
    
    def queryOne(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchone()

    def __init__(self, username, passwd, register=False):
        """User Object"""
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user='laba', password='brUQJD1sAYeQaeuJ', db='laba', cursorclass=pymysql.cursors.DictCursor, host="localhost")
        self.cursor = g.db.cursor()
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

#      |\_/|                  
#      | @ @   Watch! 
#      |   <>              _  
#      |  _/\------____ ((| |))
#      |               `--' |   
#  ____|_       ___|   |___.' 
# /_/_____/____/_______|
#^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    @property
    def id(self):
        return self.__id
    
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
        print(r)
        if not r:
            raise BadUserCredentials(self.__username)
    
    def commit(self):
        if self.__changed:
            sql="UPDATE users SET {0} WHERE users.id = {1}".format(", ".join(i+"=%s" for i in self.__changed.keys()), self.__id)
            self.query(sql, tuple(self.__changed.values()))

    def __del__(self):
        self.commit()
        self.cursor.close()
        g.db.commit()
        