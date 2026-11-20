"""
Stage 1: Order lookup agent

Build a support agent that answers questions about orders.

Requirements:

A tool lookup_order(order_id) that returns the order details from ORDERS, or an error if the order doesn’t exist.
An agent loop that keeps going until Claude gives a final answer.
A function run_agent(user_message: str) -> str that returns the final text.
"""

from main import call_claude

tools = [{
    "name": "lookup_order",
    "description": "Look up an order by its ID. Returns status, items and customer email",
    "input_schema": {
        "type": "object",
        "properties": {"order_id": {"type": "string", "description": "e.g. '1001'"}},
        "required": ["order_id"],
    }
}]

if __name__ == "__main__":
    messages = [{"role": "user", "content": "Where is my order 1001?"}]
    response = call_claude(messages, tools=tools)
    print("stop reason: ", response.stop_reason)
    print(response.model_dump_json(indent=2))

    for block in response.content:
        print(block)
