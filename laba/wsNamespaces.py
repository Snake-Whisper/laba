from flask_socketio import Namespace, emit, disconnect, join_room, leave_room, close_room, rooms
from flask import g, session, request
from user import RedisUser
from chat import Chat
from exceptions.userException import *
from exceptions.chatExceptions import *
from time import strftime
from json import loads, dumps
import pymysql

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
        session["chat"].makeChatTextEntry(msg)
        packet = {"ctime" : strftime("%d %b, %H:%M"), 
				   "content" : msg,
				   "username" : session["user"].username,
				   "chatId" : session["chat"].chat,
				  }
        print(packet)
        emit("recvPost", packet, room=str(session["chat"].chat))
    
    def on_mkChat(self, msg):
        session["chat"].recover()
        id = session["chat"].makeChat(msg)
        packet = {
            "name" : msg,
            "id" : id
        }
        print(packet)
        emit("addChat", packet)
    
    def call(self, username, event, msg):
        if not hasattr(g, 'redis'):
            g.redis = redis.Redis(host=app.config["REDIS_HOST"], port=app.config["REDIS_PORT"], db=app.config["REDIS_DB"])
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
        package = {"ctime" : strftime("%d %b, %H:%M"), 
			"content" : "{0} added you".format(session["user"].username),
			"chatId" : session["chat"].chat,
		 }
        self.call(msg, "addChatEntryBot", package)
