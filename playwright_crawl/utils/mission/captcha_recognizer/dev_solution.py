import re
import requests
from random import random
from typing import Optional

from loguru import logger
from playwright.sync_api import sync_playwright, ElementHandle

from playwright_crawl.utils.mission.captcha_recognizer.utils import resize_base64_image
from playwright_crawl.utils.mission.captcha_recognizer.captcha_resolver import CaptchaResolver
from playwright_crawl.config.settings import CAPTCHA_DEMO_URL, CAPTCHA_SINGLE_IMAGE_FILE_PATH


class Solution(object):

    def __init__(self):
        logger.debug('Captcha shows up, execute Solution...')
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)
        self.page = self.browser.new_page()
        self.page.goto(CAPTCHA_DEMO_URL)
        self.captcha_resolver = CaptchaResolver()

    def trigger_captcha(self) -> None:
        captcha_entry_frame = self.page.wait_for_selector('.h-captcha > iframe').content_frame()
        captcha_entry_frame.click('#checkbox')
        logger.debug('Click the captcha entry')

    def verify_captcha(self):
        captcha_content_frame = self.page.wait_for_selector('iframe[title*="Main content"]').content_frame()
        captcha_content_frame.wait_for_selector('.task-image .wrapper .image')
        single_captcha_elements = captcha_content_frame.locator('.task-image .wrapper .image').element_handles()
        logger.debug(single_captcha_elements[0].get_attribute('style'))
        resized_single_captcha_base64_strings = []
        for i, single_captcha_element in enumerate(single_captcha_elements):
            single_captcha_element_style = single_captcha_element.get_attribute('style')
            pattern = re.compile('url\("(https.*?)"\)')
            match_result = re.search(pattern, single_captcha_element_style)
            single_captcha_element_url = match_result.group(1) if match_result else None

            logger.debug(f'single_captcha_element_url {single_captcha_element_url}')

            with open(CAPTCHA_SINGLE_IMAGE_FILE_PATH % (i,), 'wb') as f:
                f.write(requests.get(single_captcha_element_url).content)

            resized_single_captcha_base64_string = resize_base64_image(CAPTCHA_SINGLE_IMAGE_FILE_PATH % (i,), (100, 100))
            resized_single_captcha_base64_strings.append(resized_single_captcha_base64_string)

        logger.debug(
            f'length of single_captcha_element_urls {len(resized_single_captcha_base64_strings)}')

        # try to verify using API
        captcha_recognize_result = self.captcha_resolver.create_task(
            resized_single_captcha_base64_strings,
            captcha_content_frame.wait_for_selector('.prompt-text').text_content()
        )
        if not captcha_recognize_result:
            logger.error('count not get captcha recognize result')
            return
        logger.debug(f'captcha_recognize_result {captcha_recognize_result}')
        recognized_results = captcha_recognize_result.get('solution', {}).get('objects')

        if not recognized_results:
            logger.error('count not get captcha recognized indices')
            return

        recognized_indices = [i for i, x in enumerate(recognized_results) if x]

        if len(recognized_indices) > 0:
            logger.debug(len(recognized_results))
            # click captchas
            logger.debug(f'recognized_indices {recognized_indices}')
            click_targets = captcha_content_frame.locator('.task').element_handles()
            for recognized_index in recognized_indices:
                click_targets[recognized_index].click()
                self.page.wait_for_timeout(random())

            # after all captcha clicked
            verify_button = captcha_content_frame.wait_for_selector('.button-submit')
            if verify_button.get_attribute("title") == "Next Challenge" or verify_button.get_attribute(
                    "title") == "下一个挑战":
                verify_button.click()
                self.verify_captcha()
            elif verify_button.get_attribute("title") == "Verify Answers" or verify_button.get_attribute(
                    "title") == "验证":
                verify_button.click()
        else:
            captcha_content_frame.click('.button-submit')
            self.verify_captcha()

    def resolve(self):
        self.trigger_captcha()
        self.verify_captcha()
