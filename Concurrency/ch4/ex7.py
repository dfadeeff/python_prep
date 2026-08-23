import asyncio
from ch2.ex6 import delay

async def main():
    results = await asyncio.gather(delay(3), delay(1))
    print(results)

if __name__ == "__main__":
    asyncio.run(main())