import random
import asyncio
import sys
sys.path.append('/workspace/ebay-balance-playwright')

import traceback


from playwright_crawl.config.settings import OX_PROXY, BD_PROXY, DATA_FOLDER_PATH
from playwright_crawl.utils.scheduler import Scheduler


async def main(runing_loop=1):
    success = 0
    fail = 0
    for i in range(runing_loop):
        try:
            # this_proxy = OX_PROXY.copy()
            this_proxy = BD_PROXY.copy()
            this_proxy['username'] = this_proxy['username'] % str(random.randint(20001, 29999))
            proxy_port = {'proxy': this_proxy.copy(), 'count': 4, 'port': '26600'}
            scheduler = Scheduler(
                headless=False,
                proxy=proxy_port['proxy'],
                port=proxy_port['port']
            )
            await scheduler.init_browser()
            await scheduler.register_mission()
            await scheduler.browser.close()
            success += 1
        except:
            print(traceback.format_exc())
            await scheduler.browser.close()
            fail += 1
        finally:
            print('*'*15 + f'Success: {success}, rate: {success/runing_loop}; Fail: {fail}, rate: {fail/runing_loop}'+'*'*15)

if __name__ == '__main__':
    asyncio.run(main(20))
