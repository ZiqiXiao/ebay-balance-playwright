import imaplib
import json
import os
import re
import time
from datetime import datetime, timedelta
import pytz
from faker import Faker
import random
import requests

import redis.asyncio as redis
from loguru import logger

from playwright_crawl.config.settings import DATA_FOLDER_PATH
from playwright_crawl.config.settings import EMAIL_SERVER, EMAIL_PASSWORD, EMAIL_USERNAME

def random_delay():
    return random.uniform(100, 300)


async def get_acct_info(port: str = ''):
    r = redis.Redis(db=0, decode_responses=True)
    user_list = [i for i in await r.zrange('valid_users', 0, -1, desc=True, withscores=True) if datetime.timestamp(
        datetime.now(pytz.timezone('Asia/Shanghai'))) - i[1] < 600 and port in json.loads(i[0])['port']]
    logger.debug(user_list)
    for user in user_list:
        await r.zrem('valid_users', json.dumps(json.loads(user[0])))
        await r.close()
        return user[0]


async def save_acct_info(email: str = '', port: str = ''):
    register_time = datetime.timestamp(datetime.now(pytz.timezone('Asia/Shanghai')))
    r = redis.Redis(db=0)
    user_info = {
        'email': email,
        'port': port,
    }
    await r.zadd('valid_users', {json.dumps(user_info): register_time})
    await r.close()


def get_verification_code(
    keywords: str = 'Your eBay security code', 
    email: str = '', 
    sleep_time: int = 2,
    max_retries: int = 5
    ):
    retries = 0
    time.sleep(4)
    while retries <= max_retries:
        logger.debug(f'Start Get Verification Code...')
        # 连接到 IMAP 服务器
        server = imaplib.IMAP4_SSL(EMAIL_SERVER)

        # 登录
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

        # 选择邮箱
        server.select("inbox")

        # 搜索邮件
        criteria = f'(SUBJECT "{keywords}" TO "{email}")'
        logger.debug(f'Criteria: {criteria}')
        status, messages = server.search(None, criteria)

        # 获取邮件 ID 列表
        email_ids = messages[0].split()

        # 获取最新的电子邮件 ID
        if len(email_ids) != 0:
            latest_email_id = email_ids[-1]

            # 获取邮件详情

            status, msg_data = server.fetch(latest_email_id, "(BODY[HEADER.FIELDS (SUBJECT)])")

            match = re.search(r'(?<!\d)\d{6}(?!\d)', msg_data[0][1].decode('utf-8'))
            if match:
                verification_code = match.group()
            else:
                verification_code = None

            # 关闭连接
            server.close()
            logger.info(f'Verification Code: {verification_code}')
            return verification_code
        else:
            retries += 1
            logger.debug(f'Get Verification Code Failed. Retries: {retries}')
            time.sleep(sleep_time)
            continue
    return None

def generate_email():
    faker = Faker()
    def random_substring(s, max_length=6):
            if len(s) <= max_length:
                return s
            start_index = random.randint(0, len(s) - 1 - max_length)
            end_index = start_index + max_length
            return s[start_index:end_index]

    # 生成两个随机的 email 本地部分
    email_part1 = random_substring(faker.email().split('@')[0])
    email_part2 = random_substring(faker.email().split('@')[0])

    # 生成一个随机的5位数
    random_number = str(random.randint(0, 99999))

    # 构建最终的 email 地址
    email = email_part1 + email_part2 + random_number + '@loveebay.icu'

    return email

def JM_get_token():
    JM_USERNAME = os.getenv("JM_USERNAME")
    JM_PASSWORD = os.getenv("JM_PASSWORD")
    url = f'http://api.uoomsg.com/zc/data.php?code=signIn&user={JM_USERNAME}&password={JM_PASSWORD}'
    r = requests.get(url)
    JM_TOKEN = r.content.decode('utf-8')
    os.environ.setdefault('JM_TOKEN', JM_TOKEN)

def JM_get_phone_no():
    JM_TOKEN = os.getenv("JM_TOKEN")
    url = f'http://api.uoomsg.com/zc/data.php?code=getPhone&token={JM_TOKEN}'
    r = requests.get(url)
    return r.content.decode('utf-8')

def JM_rec_text(phone_no: str, keyword: str):
    time.sleep(4)
    JM_TOKEN = os.getenv("JM_TOKEN")
    url = f'http://api.uoomsg.com/zc/data.php?code=getMsg&token={JM_TOKEN}&phone={phone_no}&keyWord={keyword}'
    r = requests.get(url)
    match = re.search(r'(?<!\d)\d{6}(?!\d)', r.content.decode('utf-8'))
    if match:
        verification_code = match.group()
    else:
        verification_code = None
    return verification_code 



