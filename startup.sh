#!/bin/bash
#uvicorn --workers 4 "fastapi-webdriver-manager.app:app" --reload
#uvicorn --workers 1 "fastapi-webdriver-manager.app:app"

# PORTS="16600" LOG_NAME='group0.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --port 9560

PORTS="16600" LOG_NAME='group0.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9560 &
PORTS="16610" LOG_NAME='group1.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9561 &
PORTS="16602" LOG_NAME='group2.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9562 &
# PORTS="16603,16613" LOG_NAME='group3.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9563 &
#PORTS="16604,16614" LOG_NAME='group4.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9564 &
#PORTS="16605,16615" LOG_NAME='group5.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9565 &
#PORTS="16606,16616" LOG_NAME='group6.log' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --host 0.0.0.0 --port 9566 &
wait