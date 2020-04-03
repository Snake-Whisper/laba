from flask_socketio import Namespace, emit, disconnect, join_room, leave_room, close_room, rooms
from flask import g, session, request
from user import RedisUser
from chat import Chat
from exceptions.userException import *
from exceptions.chatExceptions import *
from time import strftime
from json import loads, dumps
import pymysql
from redis import Redis

class ChatNamespace(Namespace):
    def __init__(self, namespace, app):
        Namespace.__init__(self, namespace)
        self.app = app
    def on_connect(self):
        print("recieved connection attemp")
        if not 'user' in g:
            try:
                session['user'] = RedisUser(self.app)
                session['chat'] = Chat(self.app, session['user'])
                #print(list(session["chat"].getChats()))
            except UserNotInitialized:
                emit("error", "chat: get lost. You are not logged in.")
                disconnect()
                return

        emit('loadChatList', list(session["chat"].getChats()))
        session["user"].wsuuid = request.sid
        for chat in session["chat"]._getChats():
            #print("adding user {0} to chat {1}".format(session["user"].username, chat) )
            join_room(str(chat))

    def on_disconnect(self):
        #TODO: fix runtime error if direct kick
        session["user"].recover()
        del session["user"].wsuuid
        session["chat"].recover()
        session.pop("user")
        session.pop("chat")
        print("recieved disconnection")

    def on_setChat(self, msg):
        try:
            session["chat"].recover()
            session["chat"].setChat(msg)
            emit("loadChatEntries", session["chat"].loadNextChatEntries())
        except NotInChat as e:
            emit('error', str(e))
    
    def on_loadNext(self):
        session["chat"].recover()
        if session["chat"].chat == -1:
            emit("error", "No chat set.")
            return
        emit("loadChatEntries", session["chat"].loadNextChatEntries())
    
    def on_sendPost(self, msg):
        session["chat"].recover()
        if session["chat"].chat == -1:
            emit("error", "no chat set.")
            return
        id = session["chat"].makeChatTextEntry(msg)
        packet = {"ctime" : strftime("%d %b, %H:%M"), 
				   "content" : msg,
				   "username" : session["user"].username,
				   "chatId" : session["chat"].chat,
                   "entryid" : id
				  }
        print(packet)
        emit("recvPost", packet, room=str(session["chat"].chat))
    
    def on_mkChat(self, msg):
        session["chat"].recover()
        id = session["chat"].makeChat(msg)
        packet = {
            "name" : msg,
            "id" : id,
            "icon" : None,
            "descript" : None
        }
        join_room(str(id))
        print(packet)
        emit("addChat", packet)
    
    def call(self, username, event, msg):
        if not hasattr(g, 'redis'):
            g.redis = Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
        sid = g.redis.get(username).decode()
        if not sid:
            return
        emit(event, msg, room=sid)
    
    def on_addMember(self, msg):
        session["chat"].recover()
        session["user"].recover()
        try:
            session["chat"].addMember(msg)
        except NotAdmin:
            emit("error", "You're not an Admin for this Chat")
            return
        except pymysql.IntegrityError:
            emit ("error", "User {0} is already member".format(msg))
            return
        package = {
            "id" : session["chat"].chat,
            "name" : session["chat"].name
        }
        self.call(msg, "addChat", package)
        print(g.redis.get(msg))
        join_room(str(session["chat"].chat), sid=g.redis.get(msg).decode())
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} added {1}".format(session["user"].username, msg),
			"chatId" : session["chat"].chat
		 }
        #self.call(msg, "addChatEntryBot", package)
        session["chat"].makeChatBotEntry("{0} added {1}".format(session["user"].username, msg))
        emit("addChatEntryBot", package, room=str(session["chat"].chat))
    
    def on_addAdmin(self, msg):
        session["chat"].recover()
        session["user"].recover()
        try:
            session["chat"].addAdmin(msg)
        except NotAdmin:
            emit("error", "You're not an Admin for this Chat")
            return
        except pymysql.IntegrityError:
            emit ("error", "User {0} is already member".format(msg))
            return
        except NotInChat:
            emit ("error", "User {0} is not a chat member".format(msg))
        package = {
            "id" : session["chat"].chat
        }
        self.call(msg, "mkAdmin", package)
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} made {1} an admin".format(session["user"].username, msg),
			"chatId" : session["chat"].chat
		 }
        session["chat"].makeChatBotEntry("{0} made {1} an Admin".format(session["user"].username, msg))
        #self.call(msg, "addChatEntryBot", package)
        emit("addChatEntryBot", package, room=str(session["chat"].chat))

    def on_listMembers(self):
        session["chat"].recover()
        if session["chat"].chat == -1:
            emit("error", "no chat set.")
            return
        package = {
            "members" : session["chat"].getMembers(),
            "admins" : session["chat"].getAdmins()
        }
        emit("listMembers", package)

    def on_delMember(self, msg):
        session["chat"].recover()
        session["user"].recover()
        if session["chat"].chat == -1:
            emit("error", "no chat set.")
            return
        try:
            session["chat"].delMember(msg)
        except NotAdmin:
            emit("error", "You're not an Admin for this Chat")
            return
        except NotInChat:
            emit("error", "Not a chat member")
            return
        package = {
            "id" : session["chat"].chat,
        }
        self.call(msg, "delChat", package)
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} deleted {1}".format(session["user"].username, msg),
			"chatId" : session["chat"].chat
		}
        session["chat"].makeChatBotEntry("{0} deleted {1}".format(session["user"].username, msg))
        emit("addChatEntryBot", package, room=str(session["chat"].chat))

    def on_delAdmin(self, msg):
        session["chat"].recover()
        session["user"].recover()
        if session["chat"].chat == -1:
            emit("error", "no chat set.")
            return
        try:
            session["chat"].delAdmin(msg)
        except NotAdmin:
            emit("error", "You're not an Admin for this Chat")
            return
        except NotInChat:
            emit("error", "Not a chat member or already droped privilegs")
            return
        package = {
            "id" : session["chat"].chat,
        }
        self.call(msg, "delAdmin", package)
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} removed admin privilegs from {1}".format(session["user"].username, msg),
			"chatId" : session["chat"].chat
		 }
        session["chat"].makeChatBotEntry("{0} removed admin privilegs from {1}".format(session["user"].username, msg))
        emit("addChatEntryBot", package, room=str(session["chat"].chat))

    def on_exitChat(self):
        session["chat"].recover()
        session["user"].recover()
        if session["chat"].chat == -1:
            emit("error", "no chat set.")
            return
        package = {
            "id" : session["chat"].chat,
        }
        self.call(session["user"].username, "delChat", package)
        leave_room(str(session["chat"].chat))
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} left {1}".format(session["user"].username, session["chat"].chat),
			"chatId" : session["chat"].chat
		}
        session["chat"].makeChatBotEntry("{0} left {1}".format(session["user"].username, session["chat"].chat))
        emit("addChatEntryBot", package, room=str(session["chat"].chat))
        session["chat"].exitChat()

    def on_setChatDescript(self, msg):
        session["user"].recover()
        session["chat"].recover()
        try:
            session["chat"].description = msg
        except NotAdmin:
            emit("error", "You are not an Admin of this chat")
            return
        session["chat"].commit2db()
        package = {
            "ctime" : strftime("%d %b, %H:%M"),
            "chatId" : session["chat"].chat,
            "description" : session["chat"].description
        }
        emit("setChatDescription", package, room=str(session["chat"].chat))
        session["chat"].makeChatBotEntry("{0} change Chatdescription".format(session["user"].username))
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} changed Description of {1}".format(session["user"].username, session["chat"].name),
			"chatId" : session["chat"].chat
		}
        emit("addChatEntryBot", package, room=str(session["chat"].chat))

    def on_setChatName(self, msg):
        session["user"].recover()
        session["chat"].recover()
        try:
            session["chat"].name = msg
        except NotAdmin:
            emit("error", "You are not an Admin of this chat")
            return
        session["chat"].commit2db()
        package = {
            "ctime" : strftime("%d %b, %H:%M"),
            "chatId" : session["chat"].chat,
            "name" : session["chat"].name
        }
        emit("setChatName", package, room=str(session["chat"].chat))
        session["chat"].makeChatBotEntry("{0} change Chat Name".format(session["user"].username))
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} changed Name of {1}".format(session["user"].username, session["chat"].name),
			"chatId" : session["chat"].chat
		}
        emit("addChatEntryBot", package, room=str(session["chat"].chat))

    def on_delPost(self, msg):
        pass
    
    #def on_setChatIcon(self, msg):
    #    xhr?
    #    pass