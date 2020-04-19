var chat;
window.onload = function ()
{
    chat = {
        currentChat : -1,
        descritps : {},
        dom : {
            chatList : document.getElementById("chatList"),
            chatEntries : document.getElementById("chatEntries")
        },
        
        craftEntry : function (content, entryid, ctime, author) {
            
            _content = document.createElement("div");
            _content.appendChild(document.createTextNode(content));
            _content.class = "content";
            
            _author = document.createElement("div");
            _author.appendChild(document.createTextNode(author));
            _author.class = "author";
            
            _ctime = document.createElement("div");
            _ctime.appendChild(document.createTextNode(ctime));
            _ctime.class = "ctime";
            
            _entry = document.createElement("div");
            _entry.appendChild(_content);
            _entry.appendChild(_author);
            _entry.appendChild(_ctime);
            _entry.class = "entry";
            _entry.id = entryid;

            return _entry;
        },

        craftFileEntry : function (content, entryid, ctime, author, name, url) {
            
            _url = document.createElement("a");
            _url.appendChild(document.createTextNode(name));
            _url.href = url;
            _url.download = name;
            _url.class = "url";

            _content = document.createElement("div");
            _content.appendChild(document.createTextNode(content));
            _content.class = "content";
            
            _author = document.createElement("div");
            _author.appendChild(document.createTextNode(author));
            _author.class = "author";
            
            _ctime = document.createElement("div");
            _ctime.appendChild(document.createTextNode(ctime));
            _ctime.class = "ctime";
            
            _entry = document.createElement("div");
            _entry.appendChild(_url);
            _entry.appendChild(_content);
            _entry.appendChild(_author);
            _entry.appendChild(_ctime);
            _entry.class = "entry";
            _entry.id = entryid;
            //_entry.style.cursor = "pointer";

            return _entry;
        },

        addChatFileEntry : function (content, entryid, ctime, author, name, url) {
            entry = this.craftFileEntry(content, entryid, ctime, author, name, url);
            this.dom.chatEntries.appendChild(entry);
        },

        loadChatFileEntry : function (content, entryid, ctime, author, name, url) {
            entry = this.craftFileEntry(content, entryid, ctime, author, name, url);
            first = this.dom.chatEntries.firstChild;
            this.dom.chatEntries.insertBefore(entry, first);
        },

        addChatEntry : function (content, entryid, ctime, author) {
            entry = this.craftEntry(content, entryid, ctime, author);
            this.dom.chatEntries.appendChild(entry);
        },

        loadChatEntry : function (content, entryid, ctime, author) {
            entry = this.craftEntry(content, entryid, ctime, author);
            first = this.dom.chatEntries.firstChild;
            this.dom.chatEntries.insertBefore(entry, first);
        },

        addChat : function (name, id, icon, descript) {
            img = document.createElement("img");
            img.src = icon;
            img.class = "chatIcon";

            chatName = document.createElement("div");
            chatName.appendChild(document.createTextNode(name));
            chatName.class = "chatName";

            this.descritps[id] = descript;

            entry = document.createElement("div");
            entry.class = "chatEntry";
            entry.appendChild(img);
            entry.appendChild(chatName);
            entry.onclick = function () {setChat(id);};
            entry.style.cursor = 'pointer';

            this.dom.chatList.appendChild(entry);
        },

        flushChat : function () {
            while (this.dom.chatEntries.firstChild) {
                this.dom.chatEntries.removeChild(this.dom.chatEntries.firstChild);
            }
        }


    }
}