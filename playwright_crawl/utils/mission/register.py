import asyncio
from random import random

from faker import Faker
from loguru import logger
from playwright.async_api import Page

from playwright_crawl.config.settings import EMAIL_PASSWORD
from playwright_crawl.utils.utils import get_verification_code


class RegisterMission(object):

    def __init__(self, page):
        self.page: Page = page
        self.faker: Faker = Faker()

    async def fill_info(self, email: str = '', password: str = EMAIL_PASSWORD):
        await self.page.wait_for_load_state('load')
        # await self.page.wait_for_timeout(5000)
        logger.debug('Filling Register Info...')
        firstname = self.faker.first_name() + self.faker.last_name()
        lastname = self.faker.last_name() + self.faker.first_name()

        # await self.page.wait_for_selector('input[id="firstname"]')
        logger.debug(f'Register with {firstname} {lastname} --- {email} --- {password}')

        await self.page.click('input[id="firstname"]')
        await self.page.type('input[id="firstname"]', firstname)
        await self.page.wait_for_timeout(random() * 1000)
        logger.debug('First Name Filled')

        await self.page.click('input[id="lastname"]')
        await self.page.type('input[id="lastname"]', lastname)
        await self.page.wait_for_timeout(random() * 1000)
        logger.debug('Last Name Filled')

        await self.page.click('input[id="Email"]')
        await self.page.type('input[id="Email"]', email)
        await self.page.wait_for_timeout(random() * 1000)
        logger.debug('Email Filled')

        await self.page.click('input[id="password"]')
        await self.page.type('input[id="password"]', password)
        await self.page.wait_for_timeout(random() * 2000)
        logger.debug('Password Filled')

        await self.page.click('#EMAIL_REG_FORM_SUBMIT')
        await self.page.wait_for_timeout(random() * 1000)
        logger.debug('Submit Clicked')

        logger.info('Register Info Submitted')

    async def fill_verification_code(self, email: str = ''):
        await self.page.wait_for_timeout(3000)
        vcode: str | None = await get_verification_code_async(email=email)

        # retries = 0
        # max_retries = 5
        if vcode is None:
            raise Exception('Verification Code Not Found! Start a new mission.')
            # while retries <= max_retries and vcode==None:
                # await self.page.click('#mainContent > div:nth-child(3) > div.module--verify-container > div:nth-child(4) > '
                #                 'div > a')
                # vcode = await get_verification_code_async(email=email, sleep_time=10, max_retries=18)

        await self.page.fill('input[id="pinbox-0"]', vcode[0])
        await self.page.wait_for_timeout(random() * 200)

        await self.page.fill('input[id="pinbox-1"]', vcode[1])
        await self.page.wait_for_timeout(random() * 200)

        await self.page.fill('input[id="pinbox-2"]', vcode[2])
        await self.page.wait_for_timeout(random() * 200)

        await self.page.fill('input[id="pinbox-3"]', vcode[3])
        await self.page.wait_for_timeout(random() * 200)

        await self.page.fill('input[id="pinbox-4"]', vcode[4])
        await self.page.wait_for_timeout(random() * 200)

        await self.page.fill('input[id="pinbox-5"]', vcode[5])
        await self.page.wait_for_timeout(random() * 200)

        logger.info('Verification Code Filled')


async def get_verification_code_async(keywords: str = 'Your eBay security code', email: str = ''):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_verification_code, keywords, email)
