#!/bin/bash

sudo gunicorn -w 4 -b 127.0.0.1:80 wsgi:app
