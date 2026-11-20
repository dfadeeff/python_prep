from main import call_claude
from stage1 import tools
from stage2 import lookup_order

if __name__ == "__main__":
    # 1. Ask Claude, it requests a tool
    messages = [{"role": "user", "content": "Where is my order 1001"}]
    response = call_claude(messages, tools=tools)
    print("1st stop_reason:", response.stop_reason)

    # 2. Save Claude's run in the history (must include the tool_use block)
    messages.append({"role": "assistant", "content": response.content})

    # 3. Find the tool request and run the function
    tool_use = next((b for b in response.content if b.type == "tool_use"), None)
    result = lookup_order(**tool_use.input)
    print("tool result", result)

    # 4. Send the result back, linked to the request by its id
    messages.append({
        "role": "user",
        "content": [{
            "type": "tool_result",
            "tool_use_id": tool_use.id,
            "content": str(result),
        }],
    })

    # 5. Ask Claude again, with the data
    final = call_claude(messages, tools=tools)
    print("2nd stop_reason:", final.stop_reason)
    print("answer: ", final.content[0].text)
