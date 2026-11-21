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
    system = """You are a patient math tutor.
    Do not directly answer a student's questions.
    Guide them to a solution step by step."""
    # Add user initial message
    add_user_message(messages, "How do I solve 5x+3=2 for x?")
    response = call_claude(messages, system=system)
    text_answer = get_text(response)
    print(text_answer)
