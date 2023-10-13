import imaplib
import json
import os
import re
import time
from datetime import datetime, timedelta

import redis.asyncio as redis
from loguru import logger

from playwright_crawl.config.settings import DATA_FOLDER_PATH
from playwright_crawl.config.settings import EMAIL_SERVER, EMAIL_PASSWORD, EMAIL_USERNAME


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
