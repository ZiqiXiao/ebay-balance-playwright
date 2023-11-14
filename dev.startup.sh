# python3 ./playwright_crawl/utils/utils.py JM_get_token
PORTS="16600" LOG_NAME='group0.log' HEADLESS='False' uvicorn "fastapi-webdriver-manager.app:app" --workers 1 --port 9560