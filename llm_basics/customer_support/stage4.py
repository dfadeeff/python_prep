from main import call_claude, ORDERS
from stage1 import tools
from stage2 import lookup_order

TOOL_FUNCTIONS = {"lookup_order": lookup_order}


def run_agent(user_message: str, max_turns: int = 10):
    messages = [{"role": "user", "content": user_message}]
    for _ in range(max_turns):
        response = call_claude(messages, tools=tools)

        # Claude is done
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Claude wants tools
        messages.append({"role": "assistant", "content": response.content})

        results = []
        for block in response.content:

            if block.type == "tool_use":
                print(f"  [tool] {block.name}({block.input})")
                func = TOOL_FUNCTIONS[block.name]
                output = func(**block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": str(output),
                })
        messages.append({"role": "user", "content": results})

    return "sorry could not find this request"


if __name__ == "__main__":
    print(run_agent("Where is my order 1001?"))
    print("---")
    print(run_agent("What's in orders 1002 and 1003?"))  # may call the tool twice
    print("---")
    print(run_agent("Where is my order?"))  # no ID -> Claude asks, no tool call
