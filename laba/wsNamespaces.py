from flask_socketio import Namespace, emit, disconnect, join_room, leave_room, close_room
from flask import g, session
from user import RedisUser
from chat import Chat
from exceptions.userException import *
from exceptions.chatExceptions import *
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
                print("accept user")
                emit('loadChatList', session["chat"].getChats())
            except UserNotInitialized:
                emit("error", "chat: get lost. You are not logged in.")
                disconnect()

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
        emit("loadChatEntries", session["chat"].loadNextChatEntries())
