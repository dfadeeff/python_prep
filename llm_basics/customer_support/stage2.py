from main import call_claude, ORDERS
from stage1 import tools

def lookup_order(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"order {order_id} not found"}
    return order


if __name__ == "__main__":
    messages = [{"role": "user", "content": "Where is my order 1001?"}]
    response = call_claude(messages, tools=tools)
    print(lookup_order("1001"))
    print(lookup_order("9999"))