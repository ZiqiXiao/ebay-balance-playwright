import os
import random

from environs import Env

env = Env()
env.read_env()

ROOT_PATH = '/Users/xiaoziqi/app-dev/parttime/bb/20230905-ebay-balance/dev'

"""
Folder Path
"""
DATA_FOLDER_PATH = os.path.join(ROOT_PATH, 'playwright_crawl/data')
CAPTCHA_ENTIRE_IMAGE_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'captcha/captcha_entire_image.png')
CAPTCHA_SINGLE_IMAGE_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'captcha/captcha_single_image_%s.png')
CAPTCHA_RESIZED_IMAGE_FILE_PATH = os.path.join(DATA_FOLDER_PATH, 'captcha/captcha_resized_image.png')

"""
URL
"""
CAPTCHA_DEMO_URL = 'https://democaptcha.com/demo-form-eng/hcaptcha.html'
SIGNIN_URL = 'https://www.ebay.com/gft/balance'

"""
Register Info
"""
EMAIL_SERVER = 'mail.nuyy.cc'
EMAIL_USERNAME = 'mail@nuyy.cc'
EMAIL_PASSWORD = 'Aa112112!'

"""
Captcha API & Key
"""
CAPTCHA_RESOLVER_API_URL = 'https://api.yescaptcha.com/createTask'
CAPTCHA_RESOLVER_API_KEY = env.str('CAPTCHA_RESOLVER_API_KEY')

"""
Proxy
"""
OX_PROXY = {
    'server': 'https://us-pr.oxylabs.io:',
    'username': 'customer-ziqix-sessid-blc',
    'password': 'Xzq062424'
}

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
}

HEADLESS = True
# HEADLESS = False
