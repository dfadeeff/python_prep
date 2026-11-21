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


# Helper functions
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)


def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)


def get_text(response):
    return "".join(b.text for b in response.content if b.type == "text")


if __name__ == "__main__":
    messages = []
    # Add user initial message
    add_user_message(messages, "Define quantum computing in one sentence")
    print("First turn, message status:", messages)
    response = call_claude(messages)
    text_answer = get_text(response)
    print(text_answer)

    # Add assistant response to messages history
    add_assistant_message(messages, text_answer)
    print("Assistant message status:", messages)
    # # Add user followup
    add_user_message(messages, "Write another sentence")
    print("Second turn, message status:", messages)
    response = call_claude(messages)
    text_answer = get_text(response)
    print(text_answer)
