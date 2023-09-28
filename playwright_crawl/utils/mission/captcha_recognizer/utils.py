from PIL import Image
import base64
from playwright_crawl.config.settings import CAPTCHA_RESIZED_IMAGE_FILE_PATH
import asyncio


async def resize_base64_image_async(filename, size):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, resize_base64_image, filename, size)


def resize_base64_image(filename, size):
    width, height = size
    img = Image.open(filename)
    new_img = img.resize((width, height))
    new_img.save(CAPTCHA_RESIZED_IMAGE_FILE_PATH)
    with open(CAPTCHA_RESIZED_IMAGE_FILE_PATH, "rb") as f:
        data = f.read()
        encoded_string = base64.b64encode(data)
        return encoded_string.decode('utf-8')
