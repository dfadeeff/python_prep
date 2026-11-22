import anthropic
from dotenv import load_dotenv

load_dotenv()
from datetime import datetime
from anthropic.types import ToolParam

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


def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


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

if __name__ == "__main__":
    messages = []
    # Add user initial message
    add_user_message(messages, "What is the exact time right now? Format it as HH:MM:SS.")
    response = call_claude(messages, tools=[get_current_datetime_schema])

    tool_use = next(b for b in response.content if b.type == "tool_use")

    result = get_current_datetime(**tool_use.input)
    print(result)

    # 1. Claude's turn, as BLOCKS
    add_assistant_message(messages, response.content)
    # 2. your result, linked by the id
    messages.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use.id,  # ← from the tool_use block
            "content": result,
            "is_error": False,
        }],
    })
    # 3. follow-up request, still including the tool schema
    final = call_claude(messages, tools=[get_current_datetime_schema])
    print(final.stop_reason)  # end_turn
    print(get_text(final))
