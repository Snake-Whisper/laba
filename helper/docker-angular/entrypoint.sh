#!/bin/bash

export NG_CLI_ANALYTICS=ci

if [ ! -d /app/laba ]; then
        echo "laba not found"
        exit -1
fi

if [ ! -d /app/angular ]; then
        echo "add angular workdir"
        mkdir /app/angular
fi

cd /app/angular

if [ ! -d /app/angular/chat-frontend ]; then
	echo "chat-frontend not found"
	echo "adding chat-frontend"
	git clone https://github.com/jannikemmerich/chat-frontend
	cd chat-frontend
	npm install .
fi

if [ ! -d /app/laba/static/chat-frontend ]; then
        mkdir /app/laba/static/chat-frontend
fi

cd /app/angular/chat-frontend
ng build --outputPath=/app/laba/static/chat-frontend

