import asyncio
import json
import os
import random
from typing import Optional

from fake_headers import Headers
from faker import Faker
from loguru import logger
from playwright.async_api import async_playwright, Page, Browser, Playwright, BrowserContext

from playwright_crawl.config.settings import SIGNIN_URL, EMAIL_PASSWORD, ROOT_PATH
from playwright_crawl.utils.mission.balance import CheckBalance
from playwright_crawl.utils.mission.captcha_recognizer.solution import Solution
from playwright_crawl.utils.mission.login import LoginMission
from playwright_crawl.utils.mission.register import RegisterMission
from playwright_stealth import stealth_async
from playwright_crawl.utils.utils import generate_email, mock_mouse_click


class Scheduler(object):
    def __init__(self,
                 headless: bool = False,
                 proxy: dict = None,
                 port: str = None,
                 reuse: bool = False):

        self.session_storage = None
        self.local_storage = None
        self.headless = headless
        self.proxy = proxy
        self.port = port
        self.reuse = reuse

        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.browser_context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.faker: Faker = Faker()

    async def init_browser(self):
        self.playwright = await async_playwright().start()

        if self.reuse:
            logger.debug(f'Reuse browser on {self.port}')
            self.browser = await self.playwright.chromium.connect_over_cdp(f'http://localhost:{self.port}')
            self.browser_context = self.browser.contexts[0]
            self.page = self.browser_context.pages[0]
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

            width = random.randint(1080, 1200)
            height = random.randint(800, 1080)

            header = Headers()
            headers = header.generate()

            self.browser_context = await self.browser.new_context(
                viewport={"width": width, "height": height},
                user_agent=headers['User-Agent'],
                timezone_id=timezone,
                locale='en-US',
                geolocation={'longitude': longitude, 'latitude': latitude}
            )
            self.page = await self.browser_context.new_page()

        await stealth_async(self.page)

        excluded_resource_types = ["stylesheet", "image", "font"] 
        async def block_aggressively(route, request): 
            if request.resource_type in excluded_resource_types and "hcaptcha" not in request.url: 
                await route.abort() 
            else: 
                await route.continue_() 
        await self.page.route("**/*", block_aggressively)

        logger.info('Init Browser Success!')


    async def register_mission(self):

        async def captcha_handler(request):
            async with captcha_semaphore:
                if "https://www.ebay.com/captcha/init" in request.url:
                    try:
                        logger.debug('Captcha Event Is Listened')
                        await Solution(page=self.page).resolve()
                    except:
                        pass

        captcha_semaphore = asyncio.Semaphore(1)

        logger.info('Start Register Mission...')
        self.page.on('request', captcha_handler)
        
        await self.page.goto(SIGNIN_URL)
        await mock_mouse_click(self.page, self.page.locator('#create-account-link'))

        register = RegisterMission(self.page)
        await register.fill_info(generate_email(), EMAIL_PASSWORD)

        login = LoginMission(self.page)
        await login.fill_personal_info()
        await self.page.wait_for_selector('input[id="redemption-code"]')
        logger.info('Login Success!')


    async def check_balance(self, gift_card_no):
        logger.info('Checking balance')
        balance = await CheckBalance(self.page).check_balance(gift_card_no)
        logger.info(f'Balance is {balance}')
        return balance

    async def close(self):
        await self.browser_context.close()
        await self.browser.close()
        await self.playwright.stop()
        logger.debug('Playwright instance destroied')
            
        

    
