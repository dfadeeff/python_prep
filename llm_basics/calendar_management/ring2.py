from dotenv import load_dotenv
import anthropic
import json

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


def run_tool(name, tool_input):
    if name == "create_calendar_event":
        return {
            "event_id": "evt_123",
            "status": "created",
            "title": tool_input["title"],
        }
    return {"error": f'Unknown tool: {name}'}


if __name__ == "__main__":
    messages = []
    add_user_message(messages,
                     "Schedule a weekly team standup every Tuesday at 9am for the next 4 weeks, starting Nov 24 2026.Invite the whole team: alice@example.com, bob@example.com, carol@example.com. Create each occurrence as a separate event, not a recurring one")
    response = call_claude(messages, tools=tools, tool_choice={"type": "auto", "disable_parallel_tool_use": True})
    # full_text = get_text(response)
    # print(full_text)
    # tool_use = next(b for b in response.content if b.type == "tool_use")
    # print("name: ", tool_use.name)
    # print("input:", tool_use.input)
    # print("id:   ", tool_use.id)

    # Loop until Claude stops asking for tools. Each iteration runs the requested
    # tool, appends the result to history, and asks Claude to continue.
    turn = 0
    while response.stop_reason == "tool_use" and turn < 15:
        tool_use = next(b for b in response.content if b.type == "tool_use")
        result = run_tool(tool_use.name, tool_use.input)

        add_assistant_message(messages, response.content)
        add_user_message(messages, [
            {
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": json.dumps(result),
            }
        ], )
        print("turn:", turn)
        turn += 1
        response = call_claude(messages, tools=tools, tool_choice={"type": "auto", "disable_parallel_tool_use": True})
    final_text = next(block for block in response.content if block.type == "text")
    print(final_text.text)
