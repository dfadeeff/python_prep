from asyncio import Future

from sympy.abc import mu

my_future = Future()

print(f"Is my_future done? {my_future.done()}")

my_future.set_result(42)

if __name__ == "__main__":
    print(f'Is my_future done? {my_future.done()}')
    print(f'What is the result of my_future? {my_future.result()}')