from flask import g, session
import pymysql
from exceptions.chatExceptions import *

class Chat():
    __counter = 0
    __currentChat = -1
    def __init__(self, app):
        assert hasattr(g, "user") and g.user.health, "Something very nesty is going on. When in Productiomode take Laba-Server immediately down and contact dev!"
        self.app = app
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
        self.__chats = self.getChats()
    
    def query(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchall()
    
    def queryOne(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchone()

    def getChats(self):
        return [i["chatid"] for i in self.query("SELECT chatid FROM chatMembers WHERE userid=%s", g.user.id)]
    
    def __contains__(self, chatId):
        if chatId in self.__chats:
            return True
        self.__chats = self.getChats() #refresh
        if chatId in self.__chats:
            return True
        return False
    
    def loadNextChatEntries(self):
        sql = """SELECT username, DATE_FORMAT(chatEntries.ctime, '%%e %%b, %%H:%%i') AS ctime, content, file
        FROM users, chatEntries
        WHERE
        chatEntries.chatID = %s AND
        users.id = chatEntries.author AND
        chatEntries.del = False
        ORDER BY chatEntries.id DESC
        LIMIT %s,%s
        """
        res = {}
        res["chatEntries"] = self.query(sql, (self.__currentChat, self.__counter, self.__counter+5))

        #WARNING: Files sorted reverse! In Js at mapping just file.pop...

        sql = """SELECT craft_url(chks, salt, %s, %s), name
        FROM files, chatEntries
        WHERE
        chatEntries.chatID = %s AND
        chatEntries.del = False
        ORDER BY chatEntries.id ASC
        LIMIT %s,%s
        """
        res["files"] = self.query(sql, (self.app.config["DATADIR"],
                        self.app.config["FILEDIR_DEEP"],
                        self.__currentChat,
                        self.__counter,
                        self.__counter+5))
        self.__counter += 5
        return res
    
    def makeChatTextEntry(self, content):
        sql = """INSERT INTO chatEntries (author, chatID, content) VALUES(%s, %s, %s, %s)"""
        self.cursor.execute(sql, (g.user.id, self.__currentChat, content))
        g.db.commit()

    def makeChatFileEntry(self, content, fileid):
        sql = """INSERT INTO chatEntries (author, chatID, content, file) VALUES(%s, %s, %s, %s)"""
        self.cursor.execute(sql, (g.user.id, self.__currentChat, content, fileid))
        g.db.commit()
    
    def makeChat(self, chatname, description):
        if len(chatname) > 50:
            raise ChatNameToLong
        sql="""INSERT INTO chats (name, owner, description) VALUES (%s, %s, %s)"""
        self.cursor.execute(sql, (chatname, g.user.id, description))
        self.cursor.execute("INSERT INTO chatMembers (userid, chatid) VALUESE (%s, %s)", (g.user.id, self.__currentChat))
        self.cursor.execute("INSERT INTO chatAdmins (userid, chatid) VALUESE (%s, %s)", (g.user.id, self.__currentChat))
        g.db.commit()
    
    def isAdmin(self):
        sql = "SELECT userid FROM chatAdmins WHERE userid=%s AND chatid=%s"
        return bool(self.queryOne(sql, (g.user.id, self.__currentChat)))
    
    def getMemebers(self):
        sql = """SELECT users.username FROM users, chatMembers WHERE chatid = %s AND users.id = chatMembers.userid"""
        return [i['username'] for i in self.query(sql, (self.__currentChat))]
    
    def addMembers(self, memberlist):
        if not self.isAdmin():
            raise NotAdmin
        data = [(x, self.__currentChat) for x in memberlist]
        #TODO: check against duplicates
        sql = "INSERT INTO chatAdmin (userid, chatid) VALUES ((SELECT id FROM users WHERE username=%s)), %s)"
        self.cursor.executemany(sql, data)
    
    #def delMembers(self, memberlist):
    #    if not self.isAdmin():
    #        raise NotAdmin
        #data = [(x, self.__currentChat) for x in memberlist]
        #TODO: check against duplicates
        #sql = "INSERT INTO chatAdmin (userid, chatid) VALUES ((SELECT id FROM users WHERE username=%s)), %s)"
        #self.cursor.executemany(sql, data)


    #@property
    #def chats(self):
    #    return self.__chats
    
    @property
    def chat(self):
        return self.__currentChat

    @chat.setter
    def chat(self, chatId):
        if chatId in self.__chats:
            self.__currentChat = chatId
            return
        self.getChats() #refresh
        if chatId in self.__chats:
            self.__currentChat = chatId
            self.__counter = 0
            return
        return NotInChat(g.user.username, chatId)