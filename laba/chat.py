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

        #WARNING: Files sorted reverse! In Js at resolution just file.pop...

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