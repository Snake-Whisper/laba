DROP table if exists chatEntries;
DROP TABLE IF EXISTS chatMembers;
DROP TABLE IF EXISTS chatAdmins;
DROP table if exists chats;
DROP table if exists users;
DROP table if exists files;

CREATE TABLE IF NOT EXISTS files (
	id INT unsigned primary key AUTO_INCREMENT,
    chks CHAR(64) NOT NULL,
	salt CHAR(10) NOT NULL,
    name varchar(50) NOT NULL,
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	compressed BOOLEAN DEFAULT FALSE NOT NULL,
	del BOOLEAN DEFAULT FALSE NOT NULL,
    UNIQUE(chks),
	INDEX(chks)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS users (
	id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL,
	password CHAR(64) NOT NULL,
	firstName VARCHAR(50) NOT NULL,
	lastName VARCHAR(50) NOT NULL,
	email VARCHAR(75) NOT NULL,
    ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    atime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    status VARCHAR(50),
    icon INT UNSIGNED REFERENCES files(id),
    enabled BOOLEAN NOT NULL DEFAULT true,
    UNIQUE (username),
    UNIQUE (email),
    INDEX (username),
    INDEX (email)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS chats (
	id INT UNSIGNED PRIMARY KEY AUTO_INCREMENT,
	name VARCHAR(50) NOT NULL,
	owner INT UNSIGNED NOT NULL,
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
    icon INT UNSIGNED DEFAULT 1 REFERENCES files(id),
    descript VARCHAR(200),
    FOREIGN KEY (owner) REFERENCES users(id)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS chatMembers (
    chatid INT UNSIGNED NOT NULL REFERENCES chats(id),
    userid INT UNSIGNED NOT NULL REFERENCES users(id),
    actor INT UNSIGNED NOT NULL REFERENCES users(id),
    ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX(chatid),
    INDEX(userid),
    UNIQUE (chatid, userid)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS chatAdmins (
    chatid INT UNSIGNED NOT NULL REFERENCES chats(id),
    userid INT UNSIGNED NOT NULL REFERENCES users(id),    
    actor INT UNSIGNED NOT NULL REFERENCES users(id),
    INDEX(chatid),
    INDEX(userid),
    UNIQUE (chatid, userid)) ENGINE=INNODB;

CREATE TABLE IF NOT EXISTS chatEntries (
	id BIGINT unsigned primary key AUTO_INCREMENT,
	author INT unsigned NOT NULL REFERENCES users(id),
	chatID INT unsigned NOT NULL REFERENCES chats(id),
	ctime TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
	file INT unsigned DEFAULT NULL REFERENCES files(id),
    del BOOLEAN DEFAULT FALSE NOT NULL,
	content TEXT,
	INDEX (chatID)) ENGINE=INNODB;

INSERT INTO users (id, username, password, firstName, lastName, email) VALUES (1, "bot", "untouchable", "Bot", "Botschinski", "Bot");
INSERT INTO files (chks, salt, name) VALUES ("bc374f77791e224c5019d4c8fa259d2c51998dba1a61b1c4ca015cdd174d64b0", "MZ2eyr4gF8", "chat.svg");
