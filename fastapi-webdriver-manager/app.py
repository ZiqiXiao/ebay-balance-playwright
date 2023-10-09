import asyncio
import json
import os
import random
import traceback
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis

from playwright_crawl.config.settings import OX_PROXY, HEADLESS
from playwright_crawl.utils.scheduler import Scheduler

PORT_LIST = os.environ.get('PORTS', '').split(',')
LOG_NAME = os.environ.get('LOG_NAME', 'logs')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')

logger.add(os.path.join('logs', LOG_NAME), rotation="1 day", retention="7 days", level='DEBUG')

PORT_DISABLED_INTERVAL = 480
PORT_RENEW_INTERVAL = PORT_DISABLED_INTERVAL + 10

r = Redis(host=REDIS_HOST, password='IamtheBest1!', db=0, decode_responses=True)


async def run_command(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode == 0:
        logger.debug(f'[{cmd!r} exited with {process.returncode}]')
        logger.debug(stdout.decode().strip())
        return True
    else:
        logger.debug(f'[{cmd!r} exited with {process.returncode}]')
        logger.debug(stderr.decode().strip())
        return False


async def active_port_monitor():
    while True:
        proxy_port_list = [i for i in await r.zrange('active_port', 0, -1, desc=True, withscores=True)
                           if json.loads(i[0])['port'] in PORT_LIST and
                           (json.loads(i[0])['count'] < 1 or (datetime.timestamp(datetime.now()) - i[1]) > PORT_DISABLED_INTERVAL)]
        for i in proxy_port_list:
            dict_i = json.loads(i[0])
            logger.debug(f'Found timeout port {dict_i["port"]}, and moving it to disabled_port')
            await run_command(f"kill -9 $(lsof -t -i :{dict_i['port']})")
            await r.zadd('disabled_port', {json.dumps(dict_i): i[1]}, nx=True)
            await r.zrem('active_port', json.dumps(dict_i))
            break
        await asyncio.sleep(2)


async def renew_port_monitor():
    async def renew_browser(proxy_str):
        proxy = json.loads(proxy_str)
        logger.debug(f'Processing {proxy}')
        await start_browser(proxy["port"])

        logger.info(f'Browser of port {proxy["port"]} is closed')

    while True:
        disable_proxy_port_list = [i for i in await r.zrange('disabled_port', 0, -1, withscores=True)
                                   if json.loads(i[0])['port'] in PORT_LIST and
                                   ((datetime.timestamp(datetime.now()) - i[1]) > PORT_RENEW_INTERVAL or
                                    json.loads(i[0])['count'] < 1)]

        if len(disable_proxy_port_list) > 0:
            for i in disable_proxy_port_list:
                # await renew_browser(i[0])
                await r.zrem('disabled_port', json.dumps(json.loads(i[0])))
                asyncio.create_task(renew_browser(i[0]))

        await asyncio.sleep(2)


@asynccontextmanager
@logger.catch
async def lifespan(app: FastAPI):
    """
    初始化Redis中关于active_port的部分。准备4个端口
    :return:
    """
    await r.flushall()

    await asyncio.gather(*[start_browser(port) for port in PORT_LIST])

    active_port_monitor_task = asyncio.create_task(active_port_monitor())
    renew_port_monitor_task = asyncio.create_task(renew_port_monitor())

    yield

    active_port_monitor_task.cancel()
    renew_port_monitor_task.cancel()
    await r.close()


app = FastAPI(lifespan=lifespan)


@app.get("/hello")
async def hello():
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"status": "success", "message": "Hello World!"})


@app.get("/start-browser")
async def start_browser(port: str):
    max_retries = 10
    retries = 0

    while retries < max_retries:
        try:
            await asyncio.sleep(2 * random.uniform(1, 2))
            logger.debug(f'Working on start browser {retries + 1} times')
            this_proxy = OX_PROXY.copy()
            this_proxy['server'] = this_proxy['server'] + str(random.randint(10001, 19999))
            this_proxy['username'] = this_proxy['username'] + str(random.randint(20001, 29999))
            proxy_port = {'proxy': this_proxy.copy(), 'count': 4, 'port': port}
            logger.debug(proxy_port)
            scheduler = Scheduler(
                headless=HEADLESS,
                proxy=proxy_port['proxy'],
                port=port,
            )
            await scheduler.init_browser()
            await scheduler.register_mission()

            create_time = datetime.timestamp(datetime.now())
            proxy_port_str = json.dumps(proxy_port)
            await r.zadd('active_port', {proxy_port_str: create_time}, nx=True)
            return
            # return JSONResponse(status_code=status.HTTP_200_OK,
            #                     content={"status": "success", "message": "Web is ready!"})
        except KeyboardInterrupt:
            break
        except Exception as e:
            retries += 1
            try:
                await scheduler.browser.close()
            except:
                logger.debug('Scheduler is not created')
            logger.debug('Terminate Browser while start browser function')
            await run_command(f"kill -9 $(lsof -t -i :{port})")
            logger.debug(traceback.format_exc())

            # return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            #                     content={"status": "error", "message": str(e)})


@app.get('/check-balance')
@logger.catch
async def check_balance(gift_card_no: str):
    try:
        if len(gift_card_no) != 13:
            return JSONResponse(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                content={"status": "error", "message": "Please Enter a 13-digits number!"})

        proxy_port_list = [i for i in await r.zrange('active_port', 0, -1, desc=False, withscores=True) if
                           json.loads(i[0])['port'] in PORT_LIST and json.loads(i[0])['count'] > 0]

        for i in proxy_port_list:
            create_time = i[1]
            dict_i = json.loads(i[0])
            logger.debug(f'Using {dict_i}')

            scheduler = Scheduler(
                headless=HEADLESS,
                proxy=dict_i['proxy'],
                port=dict_i['port'],
                reuse=True
            )
            await scheduler.init_browser()
            balance = await scheduler.check_balance(gift_card_no)

            # 更新proxy的count，重新加入active_port
            new_dict_i = dict_i.copy()
            new_dict_i['count'] -= 1
            await r.zadd('active_port', {json.dumps(new_dict_i): create_time}, nx=True)
            await r.zrem('active_port', json.dumps(dict_i))

            return JSONResponse(status_code=status.HTTP_200_OK,
                                content={"status": "success", "message": "Web is ready!", "balance": balance})

        return JSONResponse(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            content={"status": "error", "message": "No available browser! Please try again later."})
    except Exception as e:
        logger.debug(traceback.format_exc())
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            content={"status": "error", "message": str(e)})
