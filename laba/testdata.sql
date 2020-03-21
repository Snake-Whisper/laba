INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user1", md5("pwd1!"), "Gustav1", "Gans1", "user1@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user2", md5("pwd2!"), "Gustav2", "Gans2", "user2@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user3", md5("pwd3!"), "Gustav3", "Gans3", "user3@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user4", md5("pwd4!"), "Gustav4", "Gans4", "user4@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user5", md5("pwd5!"), "Gustav5", "Gans5", "user5@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user6", md5("pwd6!"), "Gustav6", "Gans6", "user6@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user7", md5("pwd7!"), "Gustav7", "Gans7", "user7@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user8", md5("pwd8!"), "Gustav8", "Gans8", "user8@web-utils.eu");
INSERT INTO users (username, password, firstName, lastName, email) VALUES ("user9", md5("pwd9!"), "Gustav9", "Gans9", "user9@web-utils.eu");

INSERT INTO chats (name, owner) VALUES ("p2pchat1", 1);
INSERT INTO chats (name, owner) VALUES ("p2pchat2", 1);
INSERT INTO chats (name, owner) VALUES ("gchat1", 1);
INSERT INTO chats (name, owner) VALUES ("gchat2", 1);
INSERT INTO chats (name, owner) VALUES ("p2pchat3", 2);
INSERT INTO chats (name, owner) VALUES ("p2pchat4", 2);
INSERT INTO chats (name, owner) VALUES ("gchat3", 2);
INSERT INTO chats (name, owner) VALUES ("gchat4", 2);


INSERT INTO chatMembers (userid, chatid) VALUES (1, 1);
INSERT INTO chatMembers (userid, chatid) VALUES (2, 1);
INSERT INTO chatMembers (userid, chatid) VALUES (1, 2);
INSERT INTO chatMembers (userid, chatid) VALUES (2, 2);

INSERT INTO chatMembers (userid, chatid) VALUES (1, 3);
INSERT INTO chatMembers (userid, chatid) VALUES (2, 3);
INSERT INTO chatMembers (userid, chatid) VALUES (3, 3);
INSERT INTO chatMembers (userid, chatid) VALUES (4, 3);
INSERT INTO chatMembers (userid, chatid) VALUES (5, 3);
INSERT INTO chatMembers (userid, chatid) VALUES (6, 3);

INSERT INTO chatMembers (userid, chatid) VALUES (1, 4);
INSERT INTO chatMembers (userid, chatid) VALUES (3, 4);
INSERT INTO chatMembers (userid, chatid) VALUES (5, 4);
INSERT INTO chatMembers (userid, chatid) VALUES (7, 4);
INSERT INTO chatMembers (userid, chatid) VALUES (9, 4);

INSERT INTO chatAdmins (userid, chatid, actor) VALUES (2, 3, 1);
INSERT INTO chatAdmins (userid, chatid, actor) VALUES (5, 3, 1);
INSERT INTO chatAdmins (userid, chatid, actor) VALUES (8, 3, 1);

INSERT INTO files (chks, salt, name, owner) VALUES ("8fe2747902e4b4b387a9af61dbcdde04d8b776f967367d52fbbd3e9c68546dca", "0123456789", "ocean.jpg", 1);
INSERT INTO files (chks, salt, name, owner) VALUES ("6b7fc370e1f1a3b0e8a5f5d7c1b878964881f04a34cb7f2820d82ba393ff6db3", "0123456789", "loewe.m4v", 1);
INSERT INTO files (chks, salt, name, owner) VALUES ("ca34b4cc927b39f9037c4de63c3d99ba4ca8ff4a9440cbd7f3a1cc1f17135f4e", "0123456789", "flask.pdf", 1);
INSERT INTO files (chks, salt, name, owner) VALUES ("f37e27e64222c8744a2f8c439e156bdd072bb3cb00bf4e6f7db40c1ad1f12512", "0123456789", "rockyou.zip", 1);
INSERT INTO files (chks, salt, name, owner) VALUES ("0a0d02157e8e1a1ef6b7eb37a68b5e68b92ea283b123a69d204bbb2fb740db4d", "0123456789", "music.mp4", 1);

INSERT INTO chatEntries (author, chatID, content) VALUES (1, 1, "NAchricht1");
INSERT INTO chatEntries (author, chatID, content) VALUES (2, 1, "NAchricht2");
INSERT INTO chatEntries (author, chatID, content) VALUES (3, 3, "GrpNAchricht1");
INSERT INTO chatEntries (author, chatID, content) VALUES (3, 3, "GrpNAchricht2");
