from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()

MODEL = "claude-sonnet-5-5"
from tools import tools


def call_claude(messages, system=None, tools=None, **extra):
    kwargs = {"messages": messages, "max_tokens": 1024, "model": MODEL}
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = tools
    kwargs.update(extra)
    return client.messages.create(**kwargs)


def get_text(resp):
    # join only accepts strings, and a block isn't a string. It's an object that contains a string.
    return "".join(block.text for block in resp.content if block.type == 'text')


def add_user_message(messages, content):
    user_message = {"role": "user", "content": content}
    messages.append(user_message)


def add_assistant_message(messages, content):
    assistant_message = {"role": "assistant", "content": content}
    messages.append(assistant_message)


if __name__ == "__main__":
    messages = []
    add_user_message(messages,
                     "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, November 23, 2026 at 10am.")
    response = call_claude(messages, tools=tools)
    full_text = get_text(response)
    print(full_text)
    tool_use = next(b for b in response.content if b.type == "tool_use")
    print("name: ", tool_use.name)
    print("input:", tool_use.input)
    print("id:   ", tool_use.id)
