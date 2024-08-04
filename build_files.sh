#!/bin/bash

# Install dependencies using the full path if necessary
/usr/local/bin/pip install -r requirements.txt

# Collect static files using the full path if necessary
/usr/local/bin/python manage.py collectstatic --noinput
