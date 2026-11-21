import anthropic
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"


def call_claude(messages, system=None, tools=None, **extra):
    kwargs = {"messages": messages, "model": MODEL, "max_tokens": 1024}
    if system:
        kwargs['system'] = system
    if tools:
        kwargs['tools'] = tools
    kwargs.update(extra)
    response = client.messages.create(**kwargs)
    return response


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "What is quantum computing? Answer in one sentence"
        }
    ]
    messages = [
        {
            "role": "user",
            "content": "Write another sentence"
        }
    ]

    response = call_claude(messages)
    #print(response.content[0].text)
    print(response)
