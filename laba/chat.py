from flask import g, session
import pymysql
from exceptions.chatExceptions import *

class Chat():
    __counter = 0
    __currentChat = -1
    def __init__(self, app, user):
        self.user = user
        self.app = app
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
        self.__chats = self._getChats()
    
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

    def _getChats(self):
        return [i["chatid"] for i in self.query("SELECT chatid FROM chatMembers WHERE userid=%s", self.user.id)]
    
    def getChats(self):
        return self.query("SELECT id, name FROM chats, chatMembers WHERE userid=%s AND chats.id=chatMembers.chatid", self.user.id)
    
    def __contains__(self, chatId):
        if chatId in self.__chats:
            return True
        self.__chats = self._getChats() #refresh
        if chatId in self.__chats:
            return True
        return False
    
    def loadNextChatEntries(self):

        res = {}

        sql = """SELECT username, DATE_FORMAT(chatEntries.ctime, '%%e %%b, %%H:%%i') AS ctime, content, file
        FROM users, chatEntries
        WHERE
        chatEntries.chatID = %s AND
        users.id = chatEntries.author AND
        chatEntries.del = False
        ORDER BY chatEntries.id DESC
        LIMIT %s,%s
        """
        
        res["chatEntries"] = self.query(sql, (self.__currentChat, self.__counter, self.app.config["CHAT_BLOCK_ROWS"]))
        #TODO: use fileFactory? Remember Cursor die....
        res["files"] = [self.queryOne("""SELECT craft_url(chks, salt, %s, %s) AS url, name FROM files WHERE id=%s""",
                               (self.app.config["DATADIR"],
                               self.app.config["FILEDIR_DEEP"],
                               entry["file"])) for entry in res["chatEntries"] if entry["file"] != None]

        self.__counter += 5
        return res
    
    def makeChatTextEntry(self, content):
        sql = """INSERT INTO chatEntries (author, chatID, content) VALUES(%s, %s, %s)"""
        self.cursor.execute(sql, (self.user.id, self.__currentChat, content))
        g.db.commit()

    def makeChatFileEntry(self, content, fileid):
        sql = """INSERT INTO chatEntries (author, chatID, content, file) VALUES(%s, %s, %s, %s)"""
        self.cursor.execute(sql, (self.user.id, self.__currentChat, content, fileid))
        g.db.commit()
    
    def makeChat(self, chatname, description):
        if len(chatname) > 50:
            raise ChatNameToLong
        sql="""INSERT INTO chats (name, owner, description) VALUES (%s, %s, %s)"""
        self.cursor.execute(sql, (chatname, self.user.id, description))
        self.cursor.execute("INSERT INTO chatMembers (userid, chatid) VALUESE (%s, %s)", (self.user.id, self.__currentChat))
        self.cursor.execute("INSERT INTO chatAdmins (userid, chatid) VALUESE (%s, %s)", (self.user.id, self.__currentChat))
        g.db.commit()
    
    def isAdmin(self):
        sql = "SELECT userid FROM chatAdmins WHERE userid=%s AND chatid=%s"
        return bool(self.queryOne(sql, (self.user.id, self.__currentChat)))
    
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
#
#    @chat.setter
#    def chat(self, chatId):
#        if chatId in self.__chats:
#            self.__currentChat = chatId
#            print("gesetzt 1")
#            return
#        self.__getChats() #refresh
#        if chatId in self.__chats:
#            self.__currentChat = chatId
#            self.__counter = 0
#            print("gesetzt 2")
#            return
#        print("chat invalid, raising")
#        return NotInChat(self.user.username, chatId)
    
    def setChat(self, chatId):
        if chatId in self.__chats:
            self.__currentChat = chatId
            self.__counter = 0
            return
        self._getChats() #refresh cache
        if chatId in self.__chats:
            self.__currentChat = chatId
            self.__counter = 0
            return
        raise NotInChat(self.user.username, chatId)