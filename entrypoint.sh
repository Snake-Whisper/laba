#!/bin/ash


while : ; do
	if nc -z db 3306; then
		echo "[ok] Database connection";
		break;
	else
		echo "wait for db";
		sleep 1;
	fi
done;

if [ ! -f /initialized ]; then
	export FLASK_APP=app.py
	cd /laba
	flask initDB
	echo "COPY"
	echo $DATADIR
	cp -r /laba/static/files/* $DATADIR
	touch /initialized
fi

/usr/bin/python3 /laba/app.py
