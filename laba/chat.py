from flask import g, session
import pymysql
from exceptions.chatException import *

class Chat():
    __values = {}
    __changed = {}
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
        return self.query("SELECT id, name, descript, get_file(icon, %s, %s) AS icon FROM chats, chatMembers WHERE userid=%s AND chats.id=chatMembers.chatid",
                        (self.app.config["DATADIR"], self.app.config["FILEDIR_DEEP"], self.user.id))
    
    def __contains__(self, chatId):
        if chatId in self.__chats:
            return True
        self.__chats = self._getChats() #refresh
        if chatId in self.__chats:
            return True
        return False
    
    def loadNextChatEntries(self):

        res = {}

        sql = """SELECT username, DATE_FORMAT(chatEntries.ctime, '%%e %%b, %%H:%%i') AS ctime, content, file, chatEntries.id AS entryid
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
        return self.cursor.lastrowid
    
    def makeChatBotEntry(self, content):
        sql = """INSERT INTO chatEntries (author, chatID, content) VALUES(1, %s, %s)"""
        self.cursor.execute(sql, (self.__currentChat, content))
        g.db.commit()

    def makeChatFileEntry(self, content, fileid):
        sql = """INSERT INTO chatEntries (author, chatID, content, file) VALUES(%s, %s, %s, %s)"""
        self.cursor.execute(sql, (self.user.id, self.__currentChat, content, fileid))
        g.db.commit()
        return self.cursor.lastrowid
    
    def makeChat(self, chatname):
        if len(chatname) > 50:
            raise ChatNameToLong
        sql="""INSERT INTO chats (name, owner) VALUES (%s, %s)"""
        self.cursor.execute(sql, (chatname, self.user.id))
        chatid = self.cursor.lastrowid
        print(chatid)
        self.cursor.execute("INSERT INTO chatMembers (userid, chatid, actor) VALUES (%s, %s, %s)", (self.user.id, chatid, self.user.id))
        self.cursor.execute("INSERT INTO chatAdmins (userid, chatid, actor) VALUES (%s, %s, %s)", (self.user.id, chatid, self.user.id))
        g.db.commit()
        return chatid
    
    def isAdmin(self):
        sql = "SELECT userid FROM chatAdmins WHERE userid=%s AND chatid=%s"
        return bool(self.queryOne(sql, (self.user.id, self.__currentChat)))
    
    def getMembers(self):
        sql = """SELECT users.username FROM users, chatMembers WHERE chatid = %s AND users.id = chatMembers.userid"""
        return [i['username'] for i in self.query(sql, (self.__currentChat))]
    
    def getAdmins(self):
        sql = """SELECT users.username FROM users, chatAdmins WHERE chatid = %s AND users.id = chatAdmins.userid"""
        return [i['username'] for i in self.query(sql, (self.__currentChat))]
    
    def addMembers(self, memberlist):
        if not self.isAdmin():
            raise NotAdmin
        data = [(x, self.__currentChat) for x in memberlist]
        #TODO: catch error at duplicates
        sql = "INSERT INTO chatMembers (userid, chatid) VALUES ((SELECT id FROM users WHERE username=%s)), %s)"
        self.cursor.executemany(sql, data)
    
    def addMember(self, member):
        if not self.isAdmin():
            print(self.user.username + "is not an Admin")
            raise NotAdmin
        #data = [(x, self.__currentChat) for x in memberlist]
        #TODO: catch error at duplicates
        sql = "INSERT INTO chatMembers (userid, chatid, actor) VALUES ((SELECT id FROM users WHERE username=%s), %s, %s)"
        self.cursor.execute(sql, (member, self.__currentChat, self.user.id))
    
    def addAdmin(self, member):
        if not self.isAdmin():
            raise NotAdmin
        if not self.queryOne("SELECT userid from chatMembers, users WHERE chatMembers.userid=users.id AND users.username=%s", member):
            raise NotInChat(member, self.chat)
        sql = "INSERT INTO chatAdmins (userid, chatid, actor) VALUES ((SELECT id FROM users WHERE username=%s), %s, %s)"
        self.cursor.execute(sql, (member, self.__currentChat, self.user.id))
    
    def delMember(self, member):
        if not self.isAdmin():
            raise NotAdmin
        sql = "DELETE FROM chatMembers WHERE chatid=%s AND userid= (SELECT id FROM users WHERE username=%s)"
        affenRows = self.cursor.execute(sql, (self.__currentChat, member))
        if not affenRows:
            raise NotInChat(member, self.chat)
    
    def delAdmin(self, member):
        if not self.isAdmin():
            raise NotAdmin
        sql = "DELETE FROM chatAdmins WHERE chatid=%s AND userid= (SELECT id FROM users WHERE username=%s)"
        affenRows = self.cursor.execute(sql, (self.__currentChat, member))
        if not affenRows:
            raise NotInChat(member, self.chat)

    def exitChat(self):
        sql = "DELETE FROM chatAdmins WHERE chatid=%s AND userid=%s"
        self.cursor.execute(sql, (self.__currentChat, self.user.id))
        sql = "DELETE FROM chatMembers WHERE chatid=%s AND userid=%s"
        self.cursor.execute(sql, (self.__currentChat, self.user.id))
        self.__chats.remove(self.__currentChat)
        self.__currentChat = -1
    
    def delEntry(self, id):
        sql="DELETE FROM chatEntries WHERE id=%s AND author=%s"
        a = self.cursor.execute(sql, (id, self.user.id))
        if not a:
            raise NotUrEntry
        

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

    def updateValues(self):
        self.__values = self.queryOne("SELECT name, owner, ctime, get_file(icon, %s, %s) as icon, descript FROM chats WHERE id=%s" , (self.app.config["DATADIR"], self.app.config["FILEDIR_DEEP"], self.__currentChat))

    @property
    def name(self):
        return self.__values["name"]
    @name.setter
    def name(self, value):
        if not self.isAdmin():
            raise NotAdmin
        if self.__values["name"] != value:
            self.__values["name"] = value
            self.__changed["name"] = value
    
    @property
    def ctime(self):
        return self.__values["ctime"]
    @property
    def author(self):
        return self.__values["author"]
    @property
    def description(self):
        return self.__values["descript"]
    @description.setter
    def description(self, value):
        if not self.isAdmin():
            raise NotAdmin
        if self.__values["descript"] != value:
            self.__values["descript"] = value
            self.__changed["descript"] = value
    
    def commit2db(self):
        if self.__changed:
            print("commiting...")
            sql="UPDATE chats SET {0} WHERE chats.id = {1}".format(", ".join(i+"=%s" for i in self.__changed.keys()), self.__currentChat)
            self.query(sql, tuple(self.__changed.values()))

    def __del__(self):
        self.commit2db()
        #print("Chat obj is going down....")
    
    @property
    def icon(self):
        return self.__values["icon"]
    
    def setChat(self, chatId):
        if chatId in self.__chats:
            self.__currentChat = chatId
            self.__counter = 0
            self.updateValues()
            return
        self.__chats = self._getChats() #refresh cache
        if chatId in self.__chats:
            self.__currentChat = chatId
            self.__counter = 0
            self.updateValues()
            return
        raise NotInChat(self.user.username, chatId)