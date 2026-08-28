import asyncio


async def coroutine_add_one(number: int) -> int:
    return number + 1


def add_one(number: int) -> int:
    return number + 1


if __name__ == "__main__":
    function_result = add_one(1)
    coroutine_result1 = asyncio.run(coroutine_add_one(1))  # creates a new event loop, explicitly runs the coroutine in the event loop
    courotine_result2 = asyncio.run(coroutine_add_one(2))  # it is intended to be the main entry point into the asyncio application we have created
    print(f'Function result is {function_result} and the type is {type(function_result)}')
    print(f'Function result is {coroutine_result1} and the type is {type(coroutine_result1)}')
    print(f'Function result is {courotine_result2} and the type is {type(courotine_result2)}')
