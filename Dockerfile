FROM alpine:3.11

MAINTAINER snake-whisper "snake-whisper@web-utils.eu"

ENV PYTHONUNBUFFERED=1

RUN echo "**** install Python and gcc ****" && \
    apk add --no-cache python3 python3-dev gcc musl-dev && \
    if [ ! -e /usr/bin/python ]; then ln -sf python3 /usr/bin/python ; fi

RUN echo "**** install pip ****" && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --no-cache --upgrade pip setuptools wheel && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi

RUN pip3 install wheel pymysql redis Flask Flask-SocketIO validate-email eventlet
COPY entrypoint.sh /
#ENTRYPOINT ["/entrypoint.sh"]
