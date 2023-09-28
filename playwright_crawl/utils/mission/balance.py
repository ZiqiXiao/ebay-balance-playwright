from loguru import logger
from playwright.async_api import Page


class CheckBalance(object):

    def __init__(self, page):
        self.page: Page = page

    async def check_balance(self, gift_card_no: str = None):
        await self.page.fill('input[id="redemption-code"]', gift_card_no)
        await self.page.click('#check-balance')
        balance = await self.page.wait_for_selector('#balance-amount')
        balance = await balance.text_content()
        logger.debug(f'balance is {balance}')
        await self.page.click('#check-another')
        return balance
