#!/bin/sh

gunicorn --config gunicorn-cfg.py spolottery.entrypoints.flaskapp:app
