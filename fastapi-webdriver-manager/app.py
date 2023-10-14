import asyncio
import json
import os
import random
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
import pytz

from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from loguru import logger
from redis.asyncio import Redis

from playwright_crawl.config.settings import OX_PROXY, SM_PROXY, HEADLESS
from playwright_crawl.utils.scheduler import Scheduler

PORT_LIST = os.environ.get('PORTS', '').split(',')
LOG_NAME = os.environ.get('LOG_NAME', 'logs')
REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
HDL = os.environ.get('HEADLESS', HEADLESS)
ENV = os.environ.get('ENV', 'dev')

if HDL.lower() == 'true':
    HDL = True
else:
    HDL = False

if ENV.lower()== 'prod':
    logger.remove(0)
logger.add(os.path.join('logs', LOG_NAME), rotation="1 day", retention="7 days", level='DEBUG')

PORT_DISABLED_INTERVAL = 600
PORT_RENEW_INTERVAL = PORT_DISABLED_INTERVAL + 10

r = Redis(host=REDIS_HOST, password='IamtheBest1!', db=0, decode_responses=True)
pw_inst = {}


async def run_command(cmd, wait_ouput=True):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    if wait_ouput:
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.debug(f'[{cmd!r} exited with {process.returncode}]')
            logger.debug(stdout.decode().strip())
            return True
        else:
            logger.debug(f'[{cmd!r} exited with {process.returncode}]')
            logger.debug(stderr.decode().strip())
            return False
    else:
        return process


async def active_port_monitor():
    while True:
        proxy_port_list = [i for i in await r.zrange('active_port', 0, -1, desc=True, withscores=True)
                           if json.loads(i[0])['port'] in PORT_LIST and
                           (json.loads(i[0])['count'] < 1 or (datetime.timestamp(datetime.now(pytz.timezone('Asia/Shanghai'))) - i[1]) > PORT_DISABLED_INTERVAL)]
        for i in proxy_port_list:
            dict_i = json.loads(i[0])
            logger.debug(f'Found timeout port {dict_i["port"]}, and moving it to disabled_port')

            if pw_inst.get(dict_i["port"]):
                scheduler = pw_inst[dict_i["port"]]
                await scheduler.close()
                scheduler = None
                logger.info(f'Browser of port {dict_i["port"]} is closed and related PW instance is cleared.')

            await r.zadd('disabled_port', {json.dumps(dict_i): i[1]}, nx=True)
            await r.zrem('active_port', json.dumps(dict_i))
            break
        await asyncio.sleep(2)


async def renew_port_monitor():
    async def renew_browser(proxy_str):
        proxy = json.loads(proxy_str)
        logger.debug(f'Processing {proxy}')
        await start_browser(proxy["port"])

    while True:
        disable_proxy_port_list = [i for i in await r.zrange('disabled_port', 0, -1, withscores=True)
                                   if json.loads(i[0])['port'] in PORT_LIST and
                                   ((datetime.timestamp(datetime.now(pytz.timezone('Asia/Shanghai'))) - i[1]) > PORT_RENEW_INTERVAL or
                                    json.loads(i[0])['count'] < 1)]

        if len(disable_proxy_port_list) > 0:
            for i in disable_proxy_port_list:
                await r.zrem('disabled_port', json.dumps(json.loads(i[0])))
                asyncio.create_task(renew_browser(i[0]))

        await asyncio.sleep(2)

async def init_start_browser(port, wait_time=10):
    await asyncio.sleep(wait_time)
    await start_browser(port)

@asynccontextmanager
@logger.catch
async def lifespan(app: FastAPI):

    await r.flushall()

    await asyncio.gather(*[init_start_browser(port, index*60) for index, port in enumerate(PORT_LIST)])

    active_port_monitor_task = asyncio.create_task(active_port_monitor())
    renew_port_monitor_task = asyncio.create_task(renew_port_monitor())

    yield

    active_port_monitor_task.cancel()
    renew_port_monitor_task.cancel()
    await r.close()


app = FastAPI(lifespan=lifespan)

# @app.get("/start-browser")
async def start_browser(port: str):
    max_retries = 10
    retries = 0
    scheduler = None

    while retries < max_retries:
        try:
            logger.debug(f'Working on start browser {retries + 1} times')

            if ENV.lower()== 'prod':
                this_proxy = SM_PROXY.copy()
                this_proxy['server'] = this_proxy['server'] % str(random.randint(10001, 10999))
            else:
                this_proxy = OX_PROXY.copy()
                this_proxy['username'] = this_proxy['username'] % str(random.randint(20001, 29999))
            
            proxy_port = {'proxy': this_proxy.copy(), 'count': 4, 'port': port}
            logger.debug(proxy_port)

            scheduler = Scheduler(
                headless=HDL,
                proxy=this_proxy,
                port=port
            )
            
            await scheduler.init_browser()
            await scheduler.register_mission()
            pw_inst[port] = scheduler
            
            create_time = datetime.timestamp(datetime.now(pytz.timezone('Asia/Shanghai')))
            proxy_port_str = json.dumps(proxy_port)
            await r.zadd('active_port', {proxy_port_str: create_time}, nx=True)
            break
            
        except Exception as e:
            retries += 1
            logger.debug('Terminate Browser while start browser function')
            if pw_inst.get(port):
                 pw_inst[port] = None
            try:
                await scheduler.close()
            except:
                pass
            logger.debug(traceback.format_exc())


@app.get("/hello")
async def hello():
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"status": "success", "message": "Hello World!"})

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

            if pw_inst.get(dict_i['port']):
                scheduler = pw_inst[dict_i['port']]
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
