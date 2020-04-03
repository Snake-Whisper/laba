#!/bin/bash

apt-get update
apt-get install -y --no-install-recommends python3-pip python3-venv git
python3 -m venv venv
. venv/bin/activate
pip3 install wheel
pip3 install --editable .
cd laba
export FLASK_APP=app.py
flask initDB
#deactivate
