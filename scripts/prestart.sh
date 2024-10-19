#!/bin/bash

set -e
set -x

python app/prestart.py
python app/initial_data.py
