import asyncio
from ch2.ex16 import async_timed
from ch2.ex6 import delay

@async_timed()
async def main() -> None:
    delay_times = [3, 3, 3]
    tasks = [asyncio.create_task(delay(seconds)) for seconds in delay_times]
    [await task for task in tasks]

if __name__ == "__main__":
    asyncio.run(main())

