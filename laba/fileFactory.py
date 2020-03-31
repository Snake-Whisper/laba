from hashlib import sha256
from flask import g, request, abort
from exceptions.userException import *
from werkzeug.utils import secure_filename
import os
import random
import string
import pymysql
import errno


class FileFactory():
    def __init__(self, app):
        #assert user.health, "Something very nesty is going on. When in Productiomode take Laba-Server immediately down and contact dev!"
        self.app = app
        if not hasattr(g, 'db'):
            g.db = pymysql.connect(user=app.config["DB_USER"], db=app.config["DB_DB"], password=app.config["DB_PWD"], host=app.config["DB_HOST"], cursorclass=pymysql.cursors.DictCursor)
        self.cursor = g.db.cursor()
    
    def query(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchall()
    
    def queryOne(self, query, param = ()):
	    self.cursor.execute(query, param)
	    return self.cursor.fetchone()

    def addFiles(self):
        if 'file[]' not in request.files:
            return abort(400)
        ids = []
        files = request.files.getlist("file[]")
        for file in files:
            filename = secure_filename (file.filename)
            if len(filename) == 0: #got bullshit -> zero filenames not supported -> risk (eg. emtpy form)
                return abort(400) #add friendly page?
            chks = sha256(file.read()).hexdigest()
            salt = ''.join([random.choice(string.ascii_letters + string.digits) for n in range(10)])
            try:
                self.query("INSERT INTO files (chks, salt, name) VALUES (%s, %s, %s)", (chks, salt, filename))
            except pymysql.IntegrityError: #it's already there
                ids.append(self.queryOne("SELECT id FROM files WHERE chks = %s", chks)['id'])
                print("Keep: "+file.filename)
                continue

            #file sin't here yet -> save
            url = self.__generate_url(chks, salt)
            file.seek(0)
            if not os.path.exists(os.path.dirname(url)):
                try:
                    os.makedirs(os.path.dirname(url))
                except OSError as exc: # Guard against race condition
                    if exc.errno != errno.EEXIST:
                        raise
                except PermissionError:
                    return abort(500)
            file.save(url)
            print("saved: "+file.filename)
            ids.append(self.queryOne("SELECT id FROM files WHERE chks = %s", chks)['id'])
        return ids
    
    def getFile(self, id):
        """returns ['name':filename, 'url':url] for file with id"""
        res = self.queryOne("""SELECT craft_url(chks, salt, %s, %s) AS url, name
                               FROM files
                               WHERE id=%s""",
                               (self.app.config["DATADIR"],
                               self.app.config["FILEDIR_DEEP"],
                               id))
        assert res, "This message should never be visible..."
        return res


    def __generate_url(self, chks, salt):
        toSplit = "/".join(chks[:self.app.config["FILEDIR_DEEP"]])
        url = os.path.join(self.app.config["DATADIR"], toSplit, chks[self.app.config["FILEDIR_DEEP"]:]+salt)
        return url
