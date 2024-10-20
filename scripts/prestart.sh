#!/bin/bash

set -e
set -x

docker-compose up -d

pip install -r requirements.txt
python -m app.prestart
python -m app.initial_data
