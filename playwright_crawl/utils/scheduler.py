import asyncio
import json
import os
import random
from typing import Optional

from fake_headers import Headers
from faker import Faker
from loguru import logger
from playwright.async_api import async_playwright, Page, Browser, Playwright

from playwright_crawl.config.settings import SIGNIN_URL, EMAIL_PASSWORD, ROOT_PATH
from playwright_crawl.utils.mission.balance import CheckBalance
from playwright_crawl.utils.mission.captcha_recognizer.solution import Solution
from playwright_crawl.utils.mission.login import LoginMission
from playwright_crawl.utils.mission.register import RegisterMission
from playwright_stealth import stealth_async


class Scheduler(object):
    def __init__(self,
                 headless: bool = False,
                 proxy: dict = None,
                 port: str = None,
                 reuse: bool = False,):

        self.session_storage = None
        self.local_storage = None
        self.headless = headless
        self.proxy = proxy
        self.port = port
        self.reuse = reuse

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.faker: Faker = Faker()

    async def init_browser(self):
        self.playwright = await async_playwright().start()

        if self.reuse:
            logger.debug(f'Reuse browser on {self.port}')
            self.browser = await self.playwright.chromium.connect_over_cdp(f'http://localhost:{self.port}')
            self.page = self.browser.contexts[0].pages[0]
        else:
            logger.debug(f'Start a new browser on {self.port}')
            self.browser = await self.playwright.chromium.launch(
                args=[
                    f'--remote-debugging-port={self.port}'],
                headless=self.headless,
                proxy=self.proxy,
            )

            timezone_data = {
                'America/New_York': {'latitude': (24.396308, 49.384358), 'longitude': (-125.000000, -66.934570)},
                'America/Chicago': {'latitude': (26.347000, 49.384358), 'longitude': (-103.002565, -84.813335)},
                'America/Denver': {'latitude': (31.332177, 49.000000), 'longitude': (-116.050003, -102.041524)},
                'America/Los_Angeles': {'latitude': (32.534306, 49.000000), 'longitude': (-125.000000, -114.130470)}
            }

            timezone = list(timezone_data.keys())[
                random.randint(0, len(timezone_data.keys()) - 1)]

            lat_range = timezone_data[timezone]['latitude']
            long_range = timezone_data[timezone]['longitude']

            latitude = round(random.uniform(lat_range[0], lat_range[1]), 6)
            longitude = round(random.uniform(long_range[0], long_range[1]), 6)

            width = random.randint(800, 900)
            height = random.randint(800, 1080)

            header = Headers()
            headers = header.generate()

            self.page = await self.browser.new_page(
                viewport={"width": width, "height": height},
                user_agent=headers['User-Agent'],
                timezone_id=timezone,
                locale='en-US',
                geolocation={'longitude': longitude, 'latitude': latitude},
                # record_video_dir=os.path.join(ROOT_PATH, 'logs')
            )

        await stealth_async(self.page)
        await self.page.route('**/*.{png,jpg,jpeg,svg,gif}', lambda route, _: route.abort())
        self.page.set_default_timeout(15000)
        logger.info('Init Browser Success!')

    async def register_mission(self):
        async def captcha_handler(request):
            nonlocal email
            async with captcha_semaphore:
                if "https://www.ebay.com/captcha/init" in request.url:
                    logger.debug('Captcha Event Is Listened')
                    await Solution(page=self.page).resolve()

        captcha_semaphore = asyncio.Semaphore(1)

        logger.info('Start Register Mission...')
        self.page.on('request', captcha_handler)

        await self.page.goto(SIGNIN_URL)
        await self.page.click('#create-account-link')

        def random_substring(s, max_length=10):
            if len(s) <= max_length:
                return s
            start_index = random.randint(0, len(s) - 1 - max_length)
            end_index = start_index + max_length
            return s[start_index:end_index]

        # 生成两个随机的 email 本地部分
        email_part1 = random_substring(self.faker.email().split('@')[0])
        email_part2 = random_substring(self.faker.email().split('@')[0])

        # 生成一个随机的5位数
        random_number = str(random.randint(0, 99999))

        # 构建最终的 email 地址
        email = email_part1 + email_part2 + random_number + '@nuyy.cc'
        password = EMAIL_PASSWORD

        register = RegisterMission(self.page)
        await register.fill_info(email, password)
        await register.fill_verification_code(email)

        login = LoginMission(self.page)
        await login.fill_personal_info()
        await self.page.wait_for_selector('input[id="redemption-code"]')
        logger.info('Login Success!')

    async def check_balance(self, gift_card_no):
        logger.info('Checking balance')
        balance = await CheckBalance(self.page).check_balance(gift_card_no)
        logger.info(f'Balance is {balance}')
        return balance
