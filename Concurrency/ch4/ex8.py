import asyncio
import aiohttp
from aiohttp import ClientSession
from ch2.ex16 import async_timed
from ch2.ex6 import delay

from util import fetch_status

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [fetch_status(session, 'https://www.example.com', 1),
                    fetch_status(session, 'https://www.example.com', 1),
                    fetch_status(session, 'https://www.example.com', 10)]
        for finished_task in asyncio.as_completed(fetchers):
            print(await finished_task)


if __name__ == "__main__":
    asyncio.run(main())