import random
import asyncio
import sys
sys.path.append('/workspace/ebay-balance-playwright')


from playwright_crawl.config.settings import OX_PROXY, DATA_FOLDER_PATH
from playwright_crawl.utils.scheduler import Scheduler


async def main():
    this_proxy = OX_PROXY.copy()
    this_proxy['username'] = this_proxy['username'] % str(random.randint(20001, 29999))
    proxy_port = {'proxy': this_proxy.copy(), 'count': 4, 'port': '26600'}
    scheduler = Scheduler(
        headless=False,
        proxy=proxy_port['proxy'],
        port=proxy_port['port']
    )
    await scheduler.init_browser()
    await scheduler.register_mission()

if __name__ == '__main__':
    asyncio.run(main())
