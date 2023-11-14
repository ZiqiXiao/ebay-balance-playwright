import os
import random

from environs import Env

env = Env()
env.read_env()


"""
Folder Path
"""
ROOT_PATH = env.str("ROOT_PATH")
DATA_FOLDER_PATH = os.path.join(ROOT_PATH, "playwright_crawl/data")
CAPTCHA_ENTIRE_IMAGE_FILE_PATH = os.path.join(
    DATA_FOLDER_PATH, "captcha/captcha_entire_image.png"
)
CAPTCHA_SINGLE_IMAGE_FILE_PATH = os.path.join(
    DATA_FOLDER_PATH, "captcha/captcha_single_image_%s.png"
)
CAPTCHA_RESIZED_IMAGE_FILE_PATH = os.path.join(
    DATA_FOLDER_PATH, "captcha/captcha_resized_image.png"
)

"""
URL
"""
CAPTCHA_DEMO_URL = "https://democaptcha.com/demo-form-eng/hcaptcha.html"
SIGNIN_URL = "https://www.ebay.com/gft/balance"

"""
Register Info
"""
EMAIL_SERVER = "mail.nuyy.cc"
EMAIL_USERNAME = "mail@nuyy.cc"
EMAIL_PASSWORD = "Aa112112!"

"""
Captcha API & Key
"""
CAPTCHA_RESOLVER_API_URL = "https://api.yescaptcha.com/createTask"
CAPTCHA_RESOLVER_API_KEY = env.str("CAPTCHA_RESOLVER_API_KEY")

"""
Proxy
"""
SM_PROXY = {
    #SP
    "server": "https://us.smartproxy.com:%s",
    "username": "sp81ef6au1",
    "password": "60qlvhIgvOi13zvGvA"
}

OX_PROXY = {
    # OX
    "server": "https://pr.oxylabs.io:7777",
    "username": "customer-ziqix-cc-us-sessid-%s-sesstime-10",
    "password": "Xzq062424"
}

BD_PROXY = {
    # BD
    "server": os.environ('BD_PROXY_SERVER'),
    "username": os.environ('BD_PROXY_USERNAME'),
    "password": os.environ('BD_PROXY_PASSWORD')
}

SM_SOCKS = {
    "server": "https://brd.superproxy.io:",
}


HEADLESS = "True"
