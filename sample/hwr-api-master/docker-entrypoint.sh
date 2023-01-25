#!/bin/bash

cd /app/static
# Collect Staticfiles
python3 /app/src/hwr_analyzer/manage.py collectstatic --noinput

cd /app/src/hwr_analyzer
# Run uvicorn (ASGI Server)
gunicorn --bind 0.0.0.0:8000 hwr_analyzer.asgi:application -k uvicorn.workers.UvicornWorker --log-level info --error-logfile - --access-logfile - --capture-output
