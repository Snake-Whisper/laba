var chat;
window.onload = function ()
{
    chat = {
        currentChat : -1,
        username : "test",
        descritps : {},
        adminForChats : [],
        dom : {
            chatList : document.getElementById("chatList"),
            chatEntries : document.getElementById("chatEntries"),
            inputField : document.getElementById("postField")
        },
        
        craftEntry : function (content, entryid, ctime, author) {

            _content = document.createElement("p");
            _content.appendChild(document.createTextNode(content));
            _content.classList.add("content");
            
            _author = document.createElement("div");
            _author.appendChild(document.createTextNode(author));
            _author.classList.add("author");
            
            _ctime = document.createElement("div");
            _ctime.appendChild(document.createTextNode(ctime));
            _ctime.classList.add("ctime");
            
            _entry = document.createElement("div");
            _entry.appendChild(_author);
            _entry.appendChild(_ctime);
            _entry.appendChild(_content);
            _entry.classList.add("entry");

            if (author == chat.username) {
                _entry.classList.add("self");
            }
            
            _entry.id = entryid;

            return _entry;
        },

        craftFileEntry : function (content, entryid, ctime, author, name, url) {
            
            _url = document.createElement("a");
            _url.appendChild(document.createTextNode(name));
            _url.href = url;
            _url.download = name;
            _url.classList.add("url");

            _content = document.createElement("p");
            _content.appendChild(document.createTextNode(content));
            _content.classList.add("content");
            
            _author = document.createElement("div");
            _author.appendChild(document.createTextNode(author));
            _author.classList.add("author");
            
            _ctime = document.createElement("div");
            _ctime.appendChild(document.createTextNode(ctime));
            _ctime.classList.add("ctime");
            
            _entry = document.createElement("div");
            _entry.appendChild(_author);
            _entry.appendChild(_ctime);
            _entry.appendChild(_url);
            _entry.appendChild(_content);
            _entry.classList.add("entry");

            if (author == chat.username) {
                _entry.classList.add("self");
            }

            _entry.id = entryid;
            //_entry.style.cursor = "pointer";

            return _entry;
        },

        addChatFileEntry : function (chatId, entryid, content, ctime, author, url, filename) {
            // NOT tested!
            if (chatId != this.currentChat) {
                console.log("marking chat" + "chatId");
                return;
            }
            entry = this.craftFileEntry(content, entryid, ctime, author, filename, url);
            this.dom.chatEntries.appendChild(entry);
            this.dom.chatEntries.lastChild.scrollIntoView();
        },

        loadChatFileEntry : function (content, entryid, ctime, author, name, url) {
            entry = this.craftFileEntry(content, entryid, ctime, author, name, url);
            first = this.dom.chatEntries.firstChild;
            this.dom.chatEntries.insertBefore(entry, first);
        },

        addChatEntry : function (chatId, entryid, content, ctime, author) {
            if (chatId != this.currentChat) {
                console.log("marking chat" + "chatId");
                return;
            }
            entry = this.craftEntry(content, entryid, ctime, author);
            this.dom.chatEntries.appendChild(entry);
            this.dom.chatEntries.lastChild.scrollIntoView();
        },

        loadChatEntry : function (content, entryid, ctime, author) {
            entry = this.craftEntry(content, entryid, ctime, author);
            first = this.dom.chatEntries.firstChild;
            this.dom.chatEntries.insertBefore(entry, first);
        },

        addChat : function (name, id, icon, descript) {
            img = document.createElement("img");
            img.src = icon;
            img.classList.add("chatIcon");

            chatName = document.createElement("div");
            chatName.appendChild(document.createTextNode(name));
            chatName.classList.add("chatName");

            this.descritps[id] = descript;

            entry = document.createElement("div");
            entry.classList.add("chatEntry");
            entry.appendChild(img);
            entry.appendChild(chatName);
            entry.onclick = function () {setChat(id);};
            entry.style.cursor = 'pointer';

            this.dom.chatList.appendChild(entry);
        },

        sendPost : function () {            
            sendPost(this.dom.inputField.value);
            this.dom.inputField.value = '';
            
        },

        addNewChat : function () {
            mkChat(this.dom.inputField.value);
            this.dom.inputField.value = '';
        },

        addBotEntry : function (chatId, content, ctime) {
            if (chatId != this.currentChat) {
                return; //not important enough for marking
            }
            _content = document.createElement("div");
            _content.appendChild(document.createTextNode(content));
            _content.classList.add("content");
            
            _author = document.createElement("div");
            _author.appendChild(document.createTextNode("Bot"));
            _author.classList.add("author");
            
            _ctime = document.createElement("div");
            _ctime.appendChild(document.createTextNode(ctime));
            _ctime.classList.add("ctime");
            
            _entry = document.createElement("div");
            _entry.appendChild(_content);
            _entry.appendChild(_author);
            _entry.appendChild(_ctime);
            _entry.classList.add("botentry");
            
            this.dom.chatList.appendChild(entry);
        },

        flushChat : function () {
            while (this.dom.chatEntries.firstChild) {
                this.dom.chatEntries.removeChild(this.dom.chatEntries.firstChild);
            }
        },

        mkAdmin : function (chatid) {
            adminForChats.push(chatid);
        },

        delAdmin : function (chatid) {
            adminForChats.shift(chatid);
        },

        delEntry : function (chatid, id) {
            if (chatid == this.currentChat) {
                document.getElementById(id).remove();                
            }
        }
    }
    socket.emit("getSelf");
}

