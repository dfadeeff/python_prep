from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

ORDERS = {
    "1001": {"status": "shipped", "items": ["Laptop stand"], "email": "anna@example.com"},
    "1002": {"status": "processing", "items": ["USB-C hub", "Cable"], "email": "anna@example.com"},
    "1003": {"status": "delivered", "items": ["Mechanical keyboard"], "email": "ben@example.com"},
    "1004": {"status": "processing", "items": ["Monitor 27\""], "email": "chris@example.com"},
}


def call_claude(messages, system=None, tools=None):
    kwargs = {"model": MODEL, "max_tokens": 1024, "messages": messages}
    if system:
        kwargs['system'] = system
    if tools:
        kwargs['tools'] = tools

    return client.messages.create(**kwargs)

# if __name__ == "__main__":
#     messages = [
#         {
#             "role": "user",
#             "content": "Hello, Claude",
#         }
#     ]
#     print(call_claude(messages))
