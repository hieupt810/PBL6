#!/bin/bash

set -e
set -x

python -m app.prestart
python -m app.initial_data
