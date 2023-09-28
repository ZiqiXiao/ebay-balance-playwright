from loguru import logger
from playwright_crawl.config.settings import CAPTCHA_RESOLVER_API_KEY, CAPTCHA_RESOLVER_API_URL
import requests
import aiohttp


class CaptchaResolver(object):

    def __init__(self, api_url=CAPTCHA_RESOLVER_API_URL, api_key=CAPTCHA_RESOLVER_API_KEY):
        self.api_url = api_url
        self.api_key = api_key

    async def create_task(self, queries, question):
        logger.debug(f'start to recognize image for question {question}')
        data = {
            "clientKey": self.api_key,
            "task": {
                "type": "HCaptchaClassification",
                "queries": queries,
                "question": question
            }
        }
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.api_url, json=data) as response:
                    result = await response.json()
                    logger.debug(f'captcha recognize result {result}')
                    return result
            except aiohttp.ClientError as e:
                logger.exception(f'error occurred while recognizing captcha: {e}')