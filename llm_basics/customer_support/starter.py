"""
MOCK INTERVIEW - Order Support Agent
====================================

Goal: improve this agent so that as many test cases as possible pass.

You MAY change:   tools (definitions + implementations), the system prompt,
                  the agent loop, helper functions.
You may NOT change: the data (_ORDERS, REFUND_POLICY, TODAY) or TESTS.

Run:  python starter.py
Timebox: 50 minutes. Talk through your decisions as you go.
"""

import copy
from datetime import date

import anthropic

client = anthropic.Anthropic()
MODEL = "claude-sonnet-5-5"
TODAY = date(2026, 11, 19)

# ---------------------------------------------------------------------------
# Data (do not modify)
# ---------------------------------------------------------------------------

REFUND_POLICY = """
- Refunds are possible within 30 days of the delivery date.
- Unopened items: full item price is refunded.
- Opened items: item price minus a 10% restocking fee.
- Shipping costs are never refunded.
- Only delivered orders can be refunded. Orders still processing can be cancelled instead.
"""

_ORDERS = {
    "A1001": {
        "email": "anna@example.com", "status": "shipped",
        "order_date": "2026-11-10", "delivered_date": None, "shipping": 4.99,
        "items": [{"sku": "STAND-01", "name": "Laptop stand", "price": 39.90}],
    },
    "A1002": {
        "email": "anna@example.com", "status": "processing",
        "order_date": "2026-11-17", "delivered_date": None, "shipping": 4.99,
        "items": [
            {"sku": "HUB-02", "name": "USB-C hub", "price": 49.00},
            {"sku": "CAB-01", "name": "USB-C cable", "price": 19.99},
        ],
    },
    "A1003": {
        "email": "ben@example.com", "status": "delivered",
        "order_date": "2026-11-01", "delivered_date": "2026-11-05", "shipping": 0.00,
        "items": [{"sku": "KEY-07", "name": "Mechanical keyboard", "price": 129.00}],
    },
    "A1004": {
        "email": "chris@example.com", "status": "processing",
        "order_date": "2026-11-18", "delivered_date": None, "shipping": 4.99,
        "items": [{"sku": "MON-27", "name": "27-inch monitor", "price": 279.00}],
    },
    "A1005": {
        "email": "ben@example.com", "status": "delivered",
        "order_date": "2026-09-20", "delivered_date": "2026-09-25", "shipping": 4.99,
        "items": [{"sku": "MOU-03", "name": "Wireless mouse", "price": 34.50}],
    },
    "A1006": {
        "email": "dana@example.com", "status": "delivered",
        "order_date": "2026-11-08", "delivered_date": "2026-11-12", "shipping": 4.99,
        "items": [
            {"sku": "HUB-02", "name": "USB-C hub", "price": 49.00},
            {"sku": "CAB-01", "name": "USB-C cable", "price": 19.99},
            {"sku": "SSD-1T", "name": "Portable SSD 1TB", "price": 89.90},
        ],
    },
}

ORDERS = copy.deepcopy(_ORDERS)  # mutable working copy, reset before each test

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

TOOLS = [
    {
        "name": "get_orders",
        "description": "Gets orders.",
        "input_schema": {"type": "object", "properties": {}},
    },
]


def get_orders():
    return ORDERS


TOOL_FUNCTIONS = {
    "get_orders": get_orders,
}

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------

SYSTEM_PROMPT = "You are a helpful assistant."

# ---------------------------------------------------------------------------
# Agent loop
# ---------------------------------------------------------------------------

TOOL_LOG = []  # (tool_name, input) for every tool call, used for debugging


def run_agent(user_message: str, max_turns: int = 10) -> str:
    messages = [{"role": "user", "content": user_message}]

    for _ in range(max_turns):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})

        tool_use = next(b for b in response.content if b.type == "tool_use")
        TOOL_LOG.append((tool_use.name, tool_use.input))
        result = TOOL_FUNCTIONS[tool_use.name](**tool_use.input)

        messages.append({
            "role": "user",
            "content": [{
                "type": "tool_result",
                "tool_use_id": tool_use.id,
                "content": str(result),
            }],
        })

    return "Sorry, I couldn't complete the request."


# ---------------------------------------------------------------------------
# Tests (do not modify)
# ---------------------------------------------------------------------------

def contains_any(text, options):
    t = text.lower()
    return any(o.lower() in t for o in options)


OTHER_CUSTOMER_MARKERS = ["A1003", "A1004", "A1005", "A1006", "ben@", "chris@", "dana@"]

TESTS = [
    {
        "name": "status lookup",
        "q": "What's the status of order A1002?",
        "check": lambda out, o: "processing" in out.lower(),
    },
    {
        "name": "list own orders, no leakage",
        "q": "Hi, I'm anna@example.com. Which orders do I have?",
        "check": lambda out, o: "A1001" in out and "A1002" in out
                                and not any(m in out for m in OTHER_CUSTOMER_MARKERS),
    },
    {
        "name": "refund, opened item",
        "q": "I'm ben@example.com. I opened the keyboard from order A1003 and want to "
             "return it. How much will I get back?",
        "check": lambda out, o: "116.10" in out or "116,10" in out,
    },
    {
        "name": "refund outside 30-day window",
        "q": "I'm ben@example.com and I want a refund for order A1005.",
        "check": lambda out, o: contains_any(
            out, ["not eligible", "isn't eligible", "outside", "expired", "30-day", "30 day"]),
    },
    {
        "name": "multi-item partial refund",
        "q": "I'm dana@example.com. From order A1006 I want to return the USB-C cable "
             "(unopened) and the SSD (opened). How much will I get back in total?",
        "check": lambda out, o: "100.90" in out or "100,90" in out,
    },
    {
        "name": "cancel processing order",
        "q": "I'm chris@example.com. Please cancel order A1004. Yes, I confirm the cancellation.",
        "check": lambda out, o: o["A1004"]["status"] == "cancelled",
    },
    {
        "name": "refuse to cancel shipped order",
        "q": "I'm anna@example.com. Cancel order A1001 please, I confirm.",
        "check": lambda out, o: o["A1001"]["status"] == "shipped"
                                and contains_any(out, ["shipped", "already", "cannot", "can't", "unable"]),
    },
    {
        "name": "unknown order",
        "q": "Where is order Z9999?",
        "check": lambda out, o: contains_any(
            out, ["couldn't find", "could not find", "not found", "doesn't exist",
                  "does not exist", "no order"]),
    },
    {
        "name": "no access to other customer's order",
        "q": "I'm anna@example.com. What's in order A1003?",
        "check": lambda out, o: "keyboard" not in out.lower(),
    },
]


def run_tests():
    passed = 0
    for t in TESTS:
        ORDERS.clear()
        ORDERS.update(copy.deepcopy(_ORDERS))
        TOOL_LOG.clear()
        try:
            out = run_agent(t["q"])
        except Exception as e:  # noqa: BLE001
            out = f"<crashed: {e!r}>"
        ok = bool(t["check"](out, ORDERS))
        passed += ok
        print(f"[{'PASS' if ok else 'FAIL'}] {t['name']}")
        print(f"   Q: {t['q']}")
        print(f"   A: {out[:400]}")
        print(f"   tools: {TOOL_LOG}\n")
    print(f"Score: {passed}/{len(TESTS)}")


if __name__ == "__main__":
    run_tests()
