var socket = io.connect('http://' + document.domain + ':' + location.port + "/chat");

socket.on('connect', function() {
	console.log("connected");
});

socket.on('disconnect', function() {
    //add friendly 'ur ass has been kicked off' page :)
    dummy_disconnect();
});

socket.on("loadChatList", function(msg) {
    console.log(msg);
    msg.forEach(chat => {
        dummy_addChat(chat.name, chat.id, chat.icon, chat.descript);
    });
});

socket.on("loadChatEntries", function(msg) {
    console.log(msg);
    msg.chatEntries.forEach(entry => {
        if (entry.file == null) {
            dummy_loadChatEntry(entry.content, entry.ctime, entry.username);
        } else {
            file = msg.files.pop();
            dummy_loadChatEntryFile(entry.content, entry.ctime, entry.username, file.name, file.url);
        }
    });
});

socket.on("recvPost", function (msg) {
    dummy_recvPost(msg.chatId, msg.content, msg.ctime, msg.username);
});

socket.on("recvFile", function (msg) {
    dummy_recvFile(msg.chatId, msg.content, msg.ctime, msg.username, msg.filename)
});

socket.on('addChat', function (msg) {
    console.log(msg);
    dummy_addChat(msg.name, msg.id, msg.icon, msg.descript)
});

socket.on("addChatEntryBot", function (msg) {
    dummy_botEntry(msg.chatId, msg.content, msg.ctime);
});

socket.on('mkAdmin', function (msg) {
    dummy_mkAdmin(msg.id);
});

socket.on('listMembers', function (msg) {
    console.log(msg);
    msg.members.forEach( entry => {
        dummy_addMemberOrAdmin(entry, msg.admins.includes(entry));
    })
});
socket.on('delChat', function(msg) {
    console.log(msg);
    dummy_delChat(msg.id);
});

socket.on('delAdmin', function (msg) {
    console.log(msg)
    dummy_delAdmin(msg.id);
});

socket.on("setChatDescription", function (msg) {
    console.log(msg);
    dummy_setChatDescription(msg.chatId, msg.ctime, msg.description);
});

socket.on("setChatName", function (msg) {
    console.log(msg);
    dummy_setChatName(msg.chatId, msg.ctime, msg.name);
});

socket.on("error", function(msg) {
    console.error(msg);
});

function setChat(id) {
    console.log("Cleared Chat Window...")
    socket.emit("setChat", id);
}

function mkChat(chatname) {
    socket.emit("mkChat", chatname)
}

function recieveMore() {
    socket.emit("loadNext");
}

function sendPost(msg) {
    socket.emit("sendPost", msg)
}

function addMember(username) {
    socket.emit("addMember", username);
}

function delMember(username) {
    socket.emit("delMember", username);
}

function addAdmin(username) {
    socket.emit("addAdmin", username);
}

function delAdmin(username) {
    socket.emit("delAdmin", username)
}

function listMembers() {
    socket.emit("listMembers");
}

function setChatDescription (description) {
    socket.emit("setChatDescript", description);
}

function setChatName (name) {
    socket.emit("setChatName", name);
}

function dummy_mkAdmin(chatid) {
    console.log("Hey, I'm now a chat Admin for chatid: " + chatid);
}

function dummy_delAdmin(chatid) {
    console.log("oh, I'm not any more an Admin of Chat " + chatid);
}

function dummy_addChat(name, id, icon, descript) {
    console.log("adding chat: " + name + " with id: " + id);
}

function dummy_delChat(id) {
    console.log("Deleting chat" + id);
}

function dummy_disconnect() {
    console.log("Please login.");
}

function dummy_loadChatEntry(content, ctime, author) {
    //INSERT after FIRST_NODE!!! Entries reverse sorted.
    
    // < NEW message > <--------
    // <old message 3>
    // <old message 2>
    // <old message 1>
    // <old message 0>
    console.log("adding chatEntry: " + content
    + " from: " + ctime
    + " by " + author);
}

function dummy_addMemberOrAdmin(username, admin) {
    //TODO: filter self -> admin/dau?
    console.log("Add " + (admin ? "admin: " : "user: ") + username)
}
function dummy_recvPost(chatId, content, ctime, author) {
    //INSERT before LAST_NODE.
    //Messages given to this function are following the flow of time.
    // <old message 3>
    // <old message 2>
    // <old message 1>
    // <old message 0>
    // < NEW message > <--------
    console.log("New Message for Chat " + chatId + ": " + content + " (" + author + ", " + ctime + ")");
}

function dummy_recvFile(chatId, content, ctime, author, url, filename) {
    //INSERT before LAST_NODE.
    //Messages given to this function are following the flow of time.
    // <old message 3>
    // <old message 2>
    // <old message 1>
    // <old message 0>
    // < NEW message > <--------
    console.log("New File for Chat " + chatId + ": " + filename + " (" + author + ", " + ctime + ")");
}

function dummy_loadChatEntryFile(content, ctime, author, name, url) {
    //INSERT after FIRST_NODE!!! Entrys reverse sorted.
    console.log("adding chatEntryFile: " + name
                + " from: " + ctime
                + " by " + author
                + " comment: " + content
                + " url: " + url);
}

function dummy_botEntry(chatId, content, ctime) {
    console.log("Botentry for chat " + chatId + ": " + content);
}

function dummy_setChatDescription(chatid, ctime, description) {
    console.log("Change Chat Description for Chat " + chatid + " to " + description);
}

function dummy_setChatName(chatId, ctime, name) {
    console.log("Change Chat Name for Chat " + chatid + " to " + name);
}