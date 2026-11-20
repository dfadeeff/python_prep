import json

from dotenv import load_dotenv
import anthropic


load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"


def call_claude(messages, system=None, tools=None):
    kwargs = {"model": MODEL, "max_tokens": 1024, "messages": messages}
    if system:
        kwargs["system"] = system

    if tools:
        kwargs["tools"] = tools

    response = client.messages.create(**kwargs)
    return response


tools = [{
    "name": "get_weather",
    "description": "Get the current weather for a given location",
    "input_schema": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": " City and state, e.g. San Francisco, CA",
            }
        },
        "required": ["location"],
    }
}]

if __name__ == "__main__":

    messages = [{"role": "user", "content": "What is the weather in San Francisco"}]
    response = call_claude(messages, tools=tools)
    tool_use = next(block for block in response.content if block.type == "tool_use")
    print(f"Claude called {tool_use.name} with {json.dumps(tool_use.input)}")