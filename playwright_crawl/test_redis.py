import asyncio
import imaplib
import re
from datetime import datetime, timedelta
from loguru import logger

import redis
from faker import Faker

from captcha_recognizer.settings import EMAIL_SERVER, EMAIL_USERNAME, EMAIL_PASSWORD


def test_redis():
    # 连接到 Redis
    r = redis.Redis(db=0)
    faker = Faker()

    # 您的用户数据
    user_data = [
        {
            "email": faker.first_name() + "@nuyy.cc",
            "register_time": str(datetime.timestamp(datetime.now()))
        },
        # ... 其他用户数据
    ]

    # 将每个用户信息添加到 'valid_users' Sorted Set 中
    r.zadd('valid_users', {user_data[0]['email']: user_data[0]['register_time']})

    # 获取分数最低（最早注册）的用户
    user_list = r.zrange('valid_users', 0, -1, withscores=True)
    for user in user_list:
        print(user[0])
        print(user[1])
        interval = datetime.timestamp(datetime.now()) - user[1]
        delta = timedelta(seconds=interval)
        if delta < timedelta(minutes=30):
            print(delta)

    # 获取分数最高（最晚注册）的用户
    latest_user = r.zrevrange('valid_users', 0, 0)
    print(f"Latest user: {latest_user}")


async def test_redis_async():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, test_redis)


def get_verification_code():
    logger.debug(f'Start Get Verification Code...')
    # 连接到 IMAP 服务器
    server = imaplib.IMAP4_SSL(EMAIL_SERVER)

    # 登录
    server.login(EMAIL_USERNAME, EMAIL_PASSWORD)

    # 选择邮箱
    server.select("inbox")

    # 搜索邮件
    status, messages = server.search(None, 'Your eBay security code')

    # 获取邮件 ID 列表
    email_ids = messages[0].split()

    # 获取最新的电子邮件 ID
    latest_email_id = email_ids[-1]

    # 获取邮件详情
    status, msg_data = server.fetch(latest_email_id, "(BODY[HEADER.FIELDS (SUBJECT)])")

    match = re.search(r'\b\d{6}\b', msg_data[0][1].decode('utf-8'))
    if match:
        verification_code = match.group()
    else:
        verification_code = None

    # 关闭连接
    server.close()
    logger.info(f'Verification Code: {verification_code}')
    return verification_code


async def get_verification_code_async():
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, get_verification_code)


asyncio.run(test_redis_async())
