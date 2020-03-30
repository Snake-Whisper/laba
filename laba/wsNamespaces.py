from flask_socketio import Namespace, emit, disconnect, join_room, leave_room, close_room
from flask import g, session, request
from user import RedisUser
from chat import Chat
from exceptions.userException import *
from exceptions.chatExceptions import *
from time import strftime
from json import loads, dumps

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
                emit('loadChatList', session["chat"].getChats())
            except UserNotInitialized:
                emit("error", "chat: get lost. You are not logged in.")
                disconnect()
                return
        #print(dir(request))
        #print(dir(session))

        session["user"].wsuuid = request.sid
        for chat in session["chat"]._getChats():
            print("adding user {0} to chat {1}".format(session["user"].username, chat) )
            join_room(str(chat))

    def on_disconnect(self):
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

