Laba-Server
===========

This server implements a simple chat server app written in python/flask.

Installation:
-------------
```bash
apt-get update
apt-get install -y --no-install-recommends python3-pip python3-venv git
git clone https://github.com/Snake-Whisper/laba
git checkout build-package
cd laba
python3 -m venv venv
. venv/bin/activate
pip3 install wheel
pip3 install -editable .
deactivate
```
Start Server
------------
```bash
. venv/bin/activate
python3 laba/app.py
```
