import json

import anthropic
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from anthropic.types import ToolParam
from anthropic.types import Message

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"


def call_claude(messages, system=None, tools=None, **extra):
    kwargs = {'model': MODEL, "max_tokens": 1024, "messages": messages}
    if system:
        kwargs['system'] = system
    if tools:
        kwargs['tools'] = tools

    kwargs.update(extra)
    response = client.messages.create(**kwargs)
    return response


def add_user_message(messages, message):
    user_message = {"role": "user",
                    "content": message.content if isinstance(message, Message) else message
                    }
    messages.append(user_message)


def add_assistant_message(messages, message):
    assistant_message = {"role": "assistant",
                         "content": message.content if isinstance(message, Message) else message
                         }
    messages.append(assistant_message)


def text_from_message(message):
    return "\n".join(
        [block.text for block in message.content if block.type == "text"]
    )


def get_text(response):
    return "".join(b.text for b in response.content if b.type == "text")


def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    if not date_format:
        raise ValueError("date_format cannot be empty")
    return datetime.now().strftime(date_format)


get_current_datetime_schema = ToolParam({
    "name": "get_current_datetime",
    "description": "Returns the current date and time formatted according to the specified format",
    "input_schema": {
        "type": "object",
        "properties": {
            "date_format": {
                "type": "string",
                "description": "A string specifying the format of the returned datetime. Uses Python's strftime format codes.",
                "default": "%Y-%m-%d %H:%M:%S"
            }
        },
        "required": []
    }
})


def run_tool(tool_name, tool_input):
    if tool_name == "get_current_datetime":
        return get_current_datetime(**tool_input)
    raise ValueError(f"Unknown tool: {tool_name}")


def run_tools(message):
    tool_requests = [block for block in message.content if block.type == "tool_use"]
    tool_result_blocks = []
    for tool_request in tool_requests:

        try:
            tool_output = run_tool(tool_request.name, tool_request.input)
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": json.dumps(tool_output),
                "is_error": False
            }
        except Exception as e:
            tool_result_block = {
                "type": "tool_result",
                "tool_use_id": tool_request.id,
                "content": f'Error:{e}',
                "is_error": True
            }

        tool_result_blocks.append(tool_result_block)
    return tool_result_blocks


def run_conversation(messages):
    while True:
        response = call_claude(messages, tools=[get_current_datetime_schema])
        add_assistant_message(messages, response)

        if response.stop_reason != "tool_use":  # Claude is done → leave the loop
            break
        tool_results = run_tools(response)  # inside the loop
        add_user_message(messages, tool_results)

    return messages


if __name__ == "__main__":
    messages = []
    add_user_message(messages, "What day is 103 days from today?")
    run_conversation(messages)

    # print the whole conversation to see each turn
    for m in messages:
        print(m["role"], "→", m["content"])
        print("---")
