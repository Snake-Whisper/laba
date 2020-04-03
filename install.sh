#!/bin/bash

export LC_ALL=C.UTF-8
export LANG=C.UTF-8
export FLASK_APP=app.py

apt-get update
apt-get install -y --no-install-recommends python3-pip python3-venv git
python3 -m venv venv
. venv/bin/activate
pip3 install wheel
pip3 install --editable .
cd laba
flask initDB
#deactivate
