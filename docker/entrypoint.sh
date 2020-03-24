#!/bin/bash

export NG_CLI_ANALYTICS=ci

if [ ! -d /app/laba ]; then
        echo "laba not found"
        exit -1
fi

if [ ! -d /app/angular/chat-frontend ]; then
	echo "chat-frontend not found"
	exit -1
fi

cd /app/angular/chat-frontend
npm install .
ng build
