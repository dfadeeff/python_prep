import asyncio
import aiohttp
from aiohttp import ClientSession
from ch2.ex16 import async_timed
from ch2.ex6 import delay

from util import fetch_status

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [fetch_status(session, 'https://example.com', 1),
        fetch_status(session, 'https://example.com', 10),
        fetch_status(session, 'https://example.com', 10)]
        for done_task in asyncio.as_completed(fetchers, timeout=2):
            try:
                result = await done_task
                print(result)
            except asyncio.TimeoutError:
                print('We got a timeout error!')
        for task in asyncio.tasks.all_tasks():
            print(task)


if __name__ == "__main__":
    asyncio.run(main())