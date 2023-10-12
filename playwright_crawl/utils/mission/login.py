import asyncio
import random

from faker import Faker
from loguru import logger
from playwright.async_api import Page

from playwright_crawl.utils.utils import get_verification_code


class LoginMission(object):

    def __init__(self, page):
        self.page: Page = page

    async def fill_username(self, username: str = None):
        logger.debug(f'Filling Username {username}')
        await self.page.fill('input[id="userid"]', username)
        await self.page.wait_for_timeout(random.random() * 1000)
        await self.page.press('input[id="userid"]', 'Enter')
        logger.debug('Username Enter Done!')

    async def fill_password(self, password: str = None):
        logger.debug('Filling Password...')
        await self.page.locator('input[id="pass"]').click(delay=random.uniform(50, 150))
        await self.page.type('input[id="pass"]', password, delay=random.uniform(100, 300))
        await self.page.wait_for_timeout(random.random() * 1000)
        await self.page.click('button[id="sgnBt"]')
        logger.debug('Password Enter Done')

    async def dont_ask_again(self):
        await self.page.click('#dont-ask-again-link')

    async def email_verification(self, email: str = ''):
        await self.page.wait_for_load_state('load')
        await self.page.evaluate('''() => {
            document.querySelector("button#emailWithCode-btn").click();
        }''')
        await self.page.wait_for_timeout(7000)
        vcode = await get_verification_code_async(email=email)

        await self.page.fill('input[id="pin-box-0"]', vcode[0])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.fill('input[id="pin-box-1"]', vcode[1])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.fill('input[id="pin-box-2"]', vcode[2])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.fill('input[id="pin-box-3"]', vcode[3])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.fill('input[id="pin-box-4"]', vcode[4])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.fill('input[id="pin-box-5"]', vcode[5])
        await self.page.wait_for_timeout(random.random() * 1000)

        await self.page.click('#verify-btn')
        logger.info('Verification Code Filled')

    async def fill_personal_info(self):
        logger.debug('Filling Personal Info...')
        faker = Faker()
        # await self.page.select_option('select[id="countryId"]', '1')
        await self.page.wait_for_load_state('load')

        address = faker.address().split('\n')[0].split(' ')[0:2]
        if len(address[0]) > 3:
            address[0] = address[0][0:3]
        address[1] = address[1].replace(',', '')

        if len(address[1]) > 4:
            address[1] = address[1][0:4]
        address = ' '.join(address)
        await self.page.locator('input[id="addressSugg"]').click(delay=random.uniform(50, 150))
        for i in address:
            await self.page.keyboard.down(i)
            await self.page.keyboard.up(i)
            await self.page.wait_for_timeout(random.random() * 300)
        logger.debug('Address Filled')

        await self.page.wait_for_timeout(random.random() * 2000)

        await self.page.locator('#addressSugg_listitem0').click(delay=random.uniform(50, 150))
        logger.debug('Address Selected')

        await self.page.wait_for_load_state('load')
        phone_no = await self.page.wait_for_selector('input[id="phoneFlagComp1"]')
        await phone_no.click(delay=random.uniform(50, 150))
        await phone_no.type('319' + '400' + faker.msisdn()[9:], delay=random.uniform(50, 150))
        logger.debug('Phone Number Filled')
        
        await self.page.wait_for_timeout(random.random()*1000)
        await self.page.locator('#sbtBtn').click(delay=random.uniform(50, 150))


async def get_verification_code_async(keyword: str = 'your security code', email: str = ''):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_verification_code, keyword, email)
