import random
import asyncio

from playwright_crawl.config.settings import OX_PROXY, DATA_FOLDER_PATH
from playwright_crawl.utils.scheduler import Scheduler


async def main():
    OX_PROXY['server'] = OX_PROXY['server'] + str(random.randint(20001, 29999))
    scheduler = Scheduler(
        headless=False,
        proxy=OX_PROXY,
        port='26600'
    )
    await scheduler.init_browser()
    await scheduler.register_mission()
    # await scheduler.login_mission()

if __name__ == '__main__':
    asyncio.run(main())
