Laba-Server DEV Version
===========

This server implements a simple chat server app written in python/flask.

Installation:
-------------
```bash
#please config laba/config
nano laba/config

#run installer
./install.sh
```
Start Server:
------------
```bash
./start.sh
```

Docker:
-------
```bash
docker-compose up
```
```bash
#For Testdata:
docker exec -it laba_app_1 /bin/ash -c 'cd /laba && flask reset'
```

surf at http://localhost:8080 

PhpMyAdmin: http://mysql.localhost:8080

RedisCommander: http://redis.localhost:8080
