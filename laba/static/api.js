var socket = io.connect('http://' + document.domain + ':' + location.port + "/chat");

socket.on('connect', function() {
	console.log("connected");
});

socket.on('disconnect', function() {
    //add friendly 'ur ass has been kicked off' page :)
    dummy_disconnect();
});

socket.on("loadChatList", function(msg) {
    msg.forEach(chat => {
        dummy_addChat(chat.name, chat.id);
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

//socket.on("addChatEntry")
//socket.on("addChatEntryBot")

socket.on("error", function(msg) {
    console.error(msg);
});

function setChat(id) {
    console.log("Cleared Chat Window...")
    socket.emit("setChat", id);
};

function RecieveMore() {
    socket.emit("loadNext");
}

function dummy_addChat(name, id) {
    console.log("adding chat: " + name + " with id: " + id);
};

function dummy_disconnect() {
    console.log("Please login.");
};

function dummy_loadChatEntry(content, ctime, author) {
    //INSERT after FIRST_NODE!!! Entries reverse sorted.
    console.log("adding chatEntry: " + content
                + " from: " + ctime
                + " by " + author);
}

function dummy_loadChatEntryFile(content, ctime, author, name, url) {
    //INSERT after FIRST_NODE!!! Entrys reverse sorted.
    console.log("adding chatEntryFile: " + name
                + " from: " + ctime
                + " by " + author
                + " comment: " + content
                + " url: " + url);
}