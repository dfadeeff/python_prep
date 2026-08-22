import asyncio
from asyncio import CancelledError
from ex6 import delay


async def main():
    long_task = asyncio.create_task(delay(10))
    second_elapsed = 0
    while not long_task.done():
        

if __name__ == "__main__":
    asyncio.run(main())
