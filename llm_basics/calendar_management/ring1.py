from dotenv import load_dotenv
import anthropic
import json

load_dotenv()
# create a client
client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"

# define one tool
tools = [
    {
        "name": "create_calendar_event",
        "description": "Create a calendar event with attendees and optioanl recurrence",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "start": {"type": "string", "format": "date-time"},
                "end": {"type": "string", "format": "date-time"},
                "attendees": {
                    "type": "array",
                    "items": {"type": "string", "format": "email"},

                },
                "recurrence": {
                    "type": "object",
                    "properties": {
                        "frequency": {"enum": ["daily", "weekly", "monthly"]},
                        "count": {"type": "integer", "minimum": 1},
                    },
                },
            },
            "required": ["title", "start", "end"],
        },
    }
]


def call_claude(messages, system=None, tools=None, **extra):
    kwargs = {"model": MODEL, "max_tokens": 1024, "messages": messages}
    if system:
        kwargs["system"] = system
    if tools:
        kwargs["tools"] = tools
    kwargs.update(extra)
    response = client.messages.create(**kwargs)
    return response


if __name__ == "__main__":
    # Send the user's request along with the tool definition. Claude determines
    # whether to call the tool based on the request and the tool description.
    messages = [
        {
            "role": "user",
            "content": "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, November 23, 2026 at 10am.",
        }
    ]
    response = call_claude(messages, tools=tools, tool_choice={"type": "auto", "disable_parallel_tool_use": True})

    # When Claude calls a tool, the response has stop_reason "tool_use"
    print(f'stop reason: {response.stop_reason}')

    # Find the tool_use block. A response might contain text blocks before the
    # tool_use block, so scan the content array rather than assuming position.
    tool_use = next(block for block in response.content if block.type == "tool_use")
    print(f"Tool: {tool_use.name}")
    print(f"Input: {tool_use.input}")

    # Run the tool. In a real system this would call your calendar API.
    # Here the result is hardcoded to keep the example self-contained.
    result = {"event_id": "evt_123", "status": "created"}

    # Send the result back. The tool_result block goes in a user message and
    # its tool_use_id must match the ID from the earlier tool_use block. The
    # assistant's previous response is included so Claude has the full history.
    messages = [

        # 1. user: the original question  ← already in messages from the first call
        {
            "role": "user",
            "content": "Schedule a 30-minute sync with alice@example.com and bob@example.com on Monday, November 23, 2026 at 10am.",
        },

        # 2. assistant: Claude's reply from call 1 (contains the tool_use request)  ← append
        {"role": "assistant", "content": response.content},

        # 3. user: your tool result, answering request #2 via tool_use_id  ← append
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                }
            ],
        },
    ]
    print(type(messages))  # check

    followup = call_claude(messages, tools=tools, tool_choice={"type": "auto", "disable_parallel_tool_use": True})

    # With the tool result, Claude produces a final natural-language
    # answer and stop_reason becomes "end_turn".
    print(f"stop_reason: {followup.stop_reason}")
    final_text = next(block for block in followup.content if block.type == "text")
    print(final_text.text)
