import asyncio
import aiohttp
from aiohttp import ClientSession
from ch2.ex16 import async_timed
from ch2.ex6 import delay
from util import fetch_status

@async_timed()
async def main() -> None:
    async with aiohttp.ClientSession() as session:
        urls = ['https://example.com' for _ in range(1000)]
        requests = [fetch_status(session, url) for url in urls]
        status_codes = await asyncio.gather(*requests)
        print(status_codes)

if __name__ == "__main__":
    asyncio.run(main())

