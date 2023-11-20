import re
import random

import requests
from loguru import logger

from playwright_crawl.config.settings import CAPTCHA_SINGLE_IMAGE_FILE_PATH
from playwright_crawl.utils.mission.captcha_recognizer.captcha_resolver import CaptchaResolver
from playwright_crawl.utils.mission.captcha_recognizer.utils import resize_base64_image_async
from playwright_crawl.utils.utils import random_delay


class Solution(object):

    def __init__(self, page, entry_selector: str = '.target-icaptcha-slot > iframe'):
        logger.debug('Captcha shows up, execute Solution...')
        self.page = page
        self.captcha_resolver = CaptchaResolver()
        self.entry_selector = entry_selector
        self.inner_frame_flag = 0

    async def trigger_captcha(self) -> None:
        try:
            captcha_entry_frame = await self.page.wait_for_selector(self.entry_selector, timeout=3000)
            captcha_entry_frame = await captcha_entry_frame.content_frame()
            await captcha_entry_frame.locator('#checkbox').click(delay=random.uniform(50, 150))
        except:
            captcha_entry_frame = self.page.frame_locator('#captchaFrame')
            captcha_entry_frame2 = await captcha_entry_frame.locator('.target-icaptcha-slot > iframe').element_handle()
            captcha_entry_frame2 = await captcha_entry_frame2.content_frame()
            await captcha_entry_frame2.locator('#checkbox').click(delay=random.uniform(50, 150))
            self.inner_frame_flag = 1

        logger.debug('Click the captcha entry')

    async def verify_captcha(self):
        if self.inner_frame_flag:
            captcha_content_frame = self.page.frame_locator('#captchaFrame')
            captcha_content_frame = await captcha_content_frame.locator('iframe[title*="Main content"]').element_handle()
        else:
            captcha_content_frame = await self.page.wait_for_selector('iframe[title*="Main content"]')
        captcha_content_frame = await captcha_content_frame.content_frame()
        await captcha_content_frame.wait_for_selector('.task-image .wrapper .image')
        single_captcha_elements = await captcha_content_frame.locator('.task-image .wrapper .image').element_handles()
        logger.debug(await single_captcha_elements[0].get_attribute('style'))
        resized_single_captcha_base64_strings = []

        for i, single_captcha_element in enumerate(single_captcha_elements):
            single_captcha_element_style = await single_captcha_element.get_attribute('style')
            pattern = re.compile('url\("(https.*?)"\)')
            match_result = re.search(pattern, single_captcha_element_style)
            single_captcha_element_url = match_result.group(1).replace('imgs2.hcaptcha.com',
                                                                       'imgs.hcaptcha.com') if match_result else None

            # logger.debug(
                # f'single_captcha_element_url {single_captcha_element_url}')

            with open(CAPTCHA_SINGLE_IMAGE_FILE_PATH % (i,), 'wb') as f:
                f.write(requests.get(single_captcha_element_url).content)

            resized_single_captcha_base64_string = await resize_base64_image_async(CAPTCHA_SINGLE_IMAGE_FILE_PATH % (
                i,), (100, 100))
            resized_single_captcha_base64_strings.append(
                resized_single_captcha_base64_string)

        # logger.debug(
            # f'length of single_captcha_element_urls {len(resized_single_captcha_base64_strings)}')

        task_text = await captcha_content_frame.wait_for_selector('.prompt-text')
        task_text = await task_text.text_content()

        # try to verify using API
        captcha_recognize_result = await self.captcha_resolver.create_task(
            resized_single_captcha_base64_strings,
            task_text
        )
        if not captcha_recognize_result:
            logger.error('count not get captcha recognize result')
            return
        logger.debug(f'captcha_recognize_result {captcha_recognize_result}')
        recognized_results = captcha_recognize_result.get(
            'solution', {}).get('objects')

        if not recognized_results:
            logger.error('count not get captcha recognized indices')
            return

        recognized_indices = [i for i, x in enumerate(recognized_results) if x]

        if len(recognized_indices) > 0:
            logger.debug(len(recognized_results))
            # click captchas
            logger.debug(f'recognized_indices {recognized_indices}')
            click_targets = await captcha_content_frame.locator('.task').element_handles()
            for recognized_index in recognized_indices:
                # await click_targets[recognized_index].click()
                box = await click_targets[recognized_index].bounding_box()
                await self.page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2, delay=random_delay())
                await self.page.wait_for_timeout(random_delay())

            # after all captcha clicked
            verify_button = await captcha_content_frame.wait_for_selector('.button-submit')
            if await verify_button.get_attribute("title") == "Next Challenge" or await verify_button.get_attribute(
                    "title") == "下一个挑战":
                verify_button.click(delay=random.uniform(50, 150))
                await self.verify_captcha()

            elif await verify_button.get_attribute("title") == "Verify Answers" or await verify_button.get_attribute(
                    "title") == "验证":
                await verify_button.click(delay=random.uniform(50, 150))
        else:
            await captcha_content_frame.click('.button-submit', delay=random.uniform(50, 150))
            await self.verify_captcha()

    async def resolve(self):
        await self.trigger_captcha()
        await self.verify_captcha()
