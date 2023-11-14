import asyncio
import random
import requests


from faker import Faker
from loguru import logger
from playwright.async_api import Page

from playwright_crawl.config.settings import EMAIL_PASSWORD
from playwright_crawl.utils.utils import get_verification_code, random_delay, JM_get_phone_no, JM_get_token, JM_rec_text


class RegisterMission(object):

    def __init__(self, page):
        self.page: Page = page
        self.faker: Faker = Faker()
        self.page.set_default_timeout(15000)

    async def fill_info(self, email: str = '', password: str = EMAIL_PASSWORD):
        await self.page.wait_for_load_state('load')
        logger.debug('Filling Register Info...')
        firstname = self.faker.first_name() + self.faker.last_name()
        lastname = self.faker.last_name() + self.faker.first_name()

        logger.debug(f'Register with {firstname} {lastname} --- {email} --- {password}')

        await self.page.locator('input[id="firstname"]').click(delay=random_delay())
        await self.page.locator('input[id="firstname"]').press_sequentially(firstname)
        # for i in firstname:
        #     await self.page.locator('input[id="firstname"]').press(i)
        #     await self.page.wait_for_timeout(random_delay())
        # await self.page.wait_for_timeout(random_delay() * 5)
        logger.debug('First Name Filled')

        await self.page.locator('input[id="lastname"]').click(delay=random_delay())
        await self.page.locator('input[id="lastname"]').press_sequentially(lastname, delay=random_delay())
        # for i in lastname:
        #     await self.page.locator('input[id="lastname"]').press(i)
        #     await self.page.wait_for_timeout(random_delay()) 
        # await self.page.wait_for_timeout(random_delay() * 5)
        logger.debug('Last Name Filled')

        await self.page.locator('input[id="Email"]').click(delay=random_delay())
        await self.page.locator('input[id="Email"]').press_sequentially(email, delay=random_delay())
        # for i in email:
        #     await self.page.locator('input[id="Email"]').press(i)
        #     await self.page.wait_for_timeout(random_delay()) 
        # await self.page.wait_for_timeout(random_delay() * 5)
        logger.debug('Email Filled')

        await self.page.locator('input[id="password"]').click(delay=random_delay())
        await self.page.locator('input[id="password"]').press_sequentially(password, delay=random_delay())
        # for i in password:
        #     await self.page.locator('input[id="password"]').press(i)
        #     await self.page.wait_for_timeout(random_delay()) 
        # await self.page.wait_for_timeout(random_delay() * 5)
        logger.debug('Password Filled')

        await self.page.locator('#EMAIL_REG_FORM_SUBMIT').click(delay=random_delay())
        await self.page.wait_for_timeout(random_delay() * 5)
        logger.debug('Submit Clicked')
        logger.info('Register Info Submitted')

        logger.debug('Phone Risk initiated, fetching verification code...')
        await self.phone_verification()

        # try:
        #     async with self.page.expect_response(lambda response: response.url == "https://signup.ebay.com/ajax/submit") as response_info:
        #         actual_response = await response_info.value  # Access the actual response object
        #         response_data = await actual_response.json()
        #         if response_data.get("isRiskInitiated"):
        #             logger.debug('Email Risk initiated, fetching verification code...')
        #             await self.fill_verification_code(email=email)
        #         elif response_data.get("isPhoneRiskInitiated"):
        #             logger.debug('Phone Risk initiated, fetching verification code...')
        #             await self.phone_verification()
        #         elif response_data.get('errorMessage'):
        #             if response_data.get('errorMessage').get('text') == 'Oops, we ran into a problem. Try again later.':
        #                 raise Exception("Encounter error msg: Oops, we ran into a problem. Try again later.")
        # except:
        #     raise Exception("Dosen't hear back after from submitting register info!")

    async def fill_verification_code(self, email: str = ''):
        vcode: str | None = await get_verification_code_async(email=email)

        if vcode is None:
            raise Exception('Verification Code Not Found! Start a new mission.')

        await self.page.fill('input[id="pinbox-0"]', vcode[0])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-1"]', vcode[1])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-2"]', vcode[2])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-3"]', vcode[3])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-4"]', vcode[4])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-5"]', vcode[5])
        await self.page.wait_for_timeout(random_delay())

        logger.info('Verification Code Filled')

    async def phone_verification(self):
        # get phone number
        phone_no = JM_get_phone_no()
        if 'ERROR:token错误，请重新通过API登录' in phone_no:
            JM_get_token()
            phone_no = JM_get_phone_no()
            if 'ERROR' in phone_no:
               raise Exception("JM API Error")
        logger.info(f'Using phone number {phone_no}')

        # choose country
        await self.page.locator('#countryCd').click(delay=random_delay())
        await self.page.get_by_text("China Mainland").click(delay=random_delay())

        # fill phone number
        await self.page.locator('input[id="phoneCountry"]').press_sequentially(phone_no, delay=random_delay())
        await self.page.click('#SEND_AUTH_CODE')

        # recieve verification code
        retry_get_phone_vcode = 3
        vcode = None
        while not vcode:
            if retry_get_phone_vcode != 0:
                vcode = await get_phone_vcode(phone_no=phone_no, keyword='ebay')
                retry_get_phone_vcode -= 1
            else:
                raise Exception(f'Not recieving valid text')

        if not vcode:
            vcode = await get_phone_vcode(phone_no=phone_no, keyword='ebay')
            if not vcode:
                raise Exception(f'vcode is not recieved by {phone_no}') 
                logger.error(f'vcode is not recieved by {phone_no}')
        logger.info(f'Vcode is {vcode}')

        # fill code
        await self.page.fill('input[id="pinbox-0"]', vcode[0])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-1"]', vcode[1])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-2"]', vcode[2])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-3"]', vcode[3])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-4"]', vcode[4])
        await self.page.wait_for_timeout(random_delay())

        await self.page.fill('input[id="pinbox-5"]', vcode[5])
        await self.page.wait_for_timeout(random_delay())

        logger.info('Verification Code Filled') 


async def get_verification_code_async(keywords: str = 'Your eBay security code', email: str = ''):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_verification_code, keywords, email)

async def get_phone_vcode(phone_no, keyword):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, JM_rec_text, phone_no, keyword) 
