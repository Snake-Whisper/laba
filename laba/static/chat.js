var chat;
window.onload = function ()
{
    chat = {
        currentChat : -1,
        username : "test",
        descritps : {},
        adminForChats : [],
        dom : {
            chatName : document.getElementById("chatName"),
            chatList : document.getElementById("chatList"),
            chatEntries : document.getElementById("chatEntries"),
            chatMembers : document.getElementById("chatMembers"),
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
                console.log("marking chat" + chatId);
                chat.markChat(chatId);
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
                console.log("marking chat" + chatId);
                chat.markChat(chatId);
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

        loadBotEntry : function (content, entryid, ctime) {
            entry = this.craftEntry(content, entryid, ctime, "bott");
            entry.classList.add("bot");
            first = this.dom.chatEntries.firstChild;
            this.dom.chatEntries.insertBefore(entry, first);
        },
        
        addChat : function (name, id, icon, descript) {
            entry = document.createElement("div");
            
            delIcon = document.createElement("div");
            delIcon.appendChild(document.createTextNode("X"));
            delIcon.classList.add("delIcon");
            delIcon.onclick = function () { chat.exitChat(id, entry); };

            img = document.createElement("img");
            img.src = icon;
            img.classList.add("chatIcon");

            chatName = document.createElement("div");
            chatName.appendChild(document.createTextNode(name));
            chatName.classList.add("chatName");

            this.descritps[id] = descript;

            entry.classList.add("chatEntry");
            entry.id = "chat" + id;
            entry.appendChild(delIcon);
            entry.appendChild(img);
            entry.appendChild(chatName);
            entry.onclick = function () { setChat(id, name); chat.unmarkChat(id); };
            entry.style.cursor = 'pointer';

            this.dom.chatList.appendChild(entry);
        },

        sendPost : function () {            
            sendPost(this.dom.inputField.value);
            this.dom.inputField.value = '';
            
        },

        addNewChat : function () {
            //mkChat(this.dom.inputField.value);
            //this.dom.inputField.value = '';

            var chat = window.prompt("Enter chat name");
            mkChat(chat);
        },

        addBotEntry : function (chatId, content, ctime) {
            console.log("add Bot Entry triggered");
            if (chatId != this.currentChat) {
                console.log("bye bot");
                return; //not important enough for marking
            }
            /*_content = document.createElement("div");
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
            
            //this.dom.chatList.appendChild(entry);
            this.dom.chatEntries.appendChild(_entry);*/
            entry = this.craftEntry(content, -1, ctime, "bott");
            entry.classList.add("bot");
            this.dom.chatEntries.appendChild(entry);
            //this.dom.chatEntries.insertBefore(entry, first);
        },

        flushChat : function () {
            while (this.dom.chatEntries.firstChild) {
                this.dom.chatEntries.removeChild(this.dom.chatEntries.firstChild);
            }
        },

        mkAdmin : function (chatid) {
            this.adminForChats.push(chatid);
            addAdmin(this.dom.inputField.value);
            this.dom.inputField.value = '';
            
        },

        delAdmin : function (chatid) {
            this.adminForChats.shift(chatid);
            delAdmin(this.dom.inputField.value);
            this.dom.inputField.value = '';
        },

        delEntry : function (chatid, id) {
            if (chatid == this.currentChat) {
                document.getElementById(id).remove();                
            }
        },

        addMember : function () {
            //addMember(this.dom.inputField.value);
            //this.dom.inputField.value = '';

            var member = window.prompt("Enter username");

            if(member != null) {
                addMember(member);
                listMembers();
            }
        },

        delMember : function () {
            delMember(this.dom.inputField.value);
            this.dom.inputField.value = '';
        },

        exitChat : function(id, element) {
            if (!confirm("sure?")) {
                return;
            }
            exitChat(id);
            console.log(element);
            element.remove();
            //setChat(-1);
        },

        hideMemberList : function() {
            this.dom.chatMembers.style.visibility = "hidden";
        },

        showMemberList : function() {
            listMembers();
            this.dom.chatMembers.style.visibility = "visible";
        },

        toggleMemberList : function() {
            this.dom.chatMembers.style.visibility = this.dom.chatMembers.style.visibility == "hidden" ? this.showMemberList() : this.hideMemberList();
        },

        clearMemberList : function() {
            Array.from(this.dom.chatMembers.children).forEach(member => {
                if(Array.from(member.classList).includes("member-entry")) {
                    this.dom.chatMembers.removeChild(member);
                }
            });
        },

        addMemberOrAdmin : function(username, admin) {
            _memberEntry = document.createElement("div");
            _memberEntry.classList.add("member-entry");

            _delete = document.createElement("div");
            _delete.classList.add("delIcon");
            _delete.appendChild(document.createTextNode("X"));
            _delete.onclick = function() { delMember(username); listMembers(); };

            _admin = document.createElement("div");
            _admin.classList.add("mkAdmin");
            _admin.appendChild(document.createTextNode(admin ? "Remove Admin" : "Make Admin"));
            _admin.onclick = function() { admin ? delAdmin(username) : addAdmin(username); listMembers(); };

            _member = document.createElement("div");
            _member.classList.add("chat-member");
            _member.appendChild(document.createTextNode(username));

            if(admin) {
                _member.classList.add("chat-admin");
                _admin.classList.add("delAdmin");
            }

            _memberEntry.appendChild(_delete);
            _memberEntry.appendChild(_admin);
            _memberEntry.appendChild(_member);

            this.dom.chatMembers.appendChild(_memberEntry);
        },

        markChat : function(id) {
            var chat = document.getElementById("chat" + id);

            chat.classList.add("marked");
        },

        unmarkChat : function(id) {
            var chat = document.getElementById("chat" + id);

            chat.classList.remove("marked");
        }
    }
    socket.emit("getSelf");
}

