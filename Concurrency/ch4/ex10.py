import asyncio
import aiohttp
from aiohttp import ClientSession
from ch2.ex16 import async_timed
from ch2.ex6 import delay

from util import fetch_status

@async_timed()
async def main():
    async with aiohttp.ClientSession() as session:
        fetchers = [asyncio.create_task(fetch_status(session, 'https://example.com')), asyncio.create_task(fetch_status(session, 'https://example.com'))]
        done, pending = await asyncio.wait(fetchers)

        print(f'Done task count: {len(done)}')
        print(f'Pending task count: {len(pending)}')

        for done_task in done:
            result = await done_task
        print(result)


if __name__ == "__main__":
    asyncio.run(main())