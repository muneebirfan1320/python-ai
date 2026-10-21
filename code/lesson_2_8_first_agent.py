
"""Lesson 2.8: Your First Agent for Sweet Crumbs Bakery."""

import json
from pathlib import Path

from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from pydantic import ValidationError

# Stop the agent if it keeps requesting tools.
MAX_STEPS = 5

# This file stores orders next to this Python script.
ORDERS_FILE = Path(__file__).resolve().parent / "agent_orders.json"

# Bakery data used by our Python tools.
PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
}

ORDERS = {
    "A101": "baking",
    "A102": "out for delivery",
    "A103": "delivered",
}


@tool(parse_docstring=True)
def get_price(item: str) -> str:
    """Get the price of one bakery item.

    Args:
        item: Bakery item name, such as cupcake or brownie.
    """
    name = item.lower().strip()

    if name in PRICES:
        return f"{name} costs {PRICES[name]} PKR"

    return f"{item} is not on the menu. Menu: {', '.join(PRICES)}"


@tool(parse_docstring=True)
def order_status(order_id: str) -> str:
    """Check the delivery status of an existing order.

    Args:
        order_id: The order number, such as A101 or A102.
    """
    key = order_id.upper().strip()

    if key not in ORDERS:
        return f"Order {key} was not found."

    return f"Order {key} is {ORDERS[key]}."


@tool(parse_docstring=True)
def place_order(item: str, quantity: int, customer: str) -> str:
    """Prepare a bakery order after the customer requests it.

    Always ask the human owner for approval before saving an order.

    Args:
        item: Bakery item name, such as cupcake or brownie.
        quantity: Number of items requested. Must be a positive integer.
        customer: Name of the customer placing the order.
    """
    name = item.lower().strip()
    customer = customer.strip()

    # Check the input before doing anything.
    if name not in PRICES:
        return f"{item} is not on the menu."

    if quantity < 1:
        return "Quantity must be at least 1."

    if not customer:
        return "A customer name is required."

    # Python calculates the total to avoid relying on AI maths.
    total = PRICES[name] * quantity

    # A human must approve an action that creates an order.
    approval = input(
        f"\n[APPROVAL] {customer}: {quantity} x {name} "
        f"= {total} PKR. Place this order? (yes/no): "
    )

    if approval.strip().lower() != "yes":
        return "Order was not placed. Owner did not approve it."

    # Find a new ID without overwriting an existing order.
    number = 101
    while f"A{number}" in ORDERS:
        number += 1

    order_id = f"A{number}"
    order_data = {
        "id": order_id,
        "item": name,
        "quantity": quantity,
        "customer": customer,
        "total": total,
    }

    # Save the approved order to a JSON file.
    with ORDERS_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(order_data) + "\n")

    ORDERS[order_id] = "received"

    return (
        f"Order {order_id} placed successfully: "
        f"{quantity} x {name}, total {total} PKR."
    )


# The model can choose only these three tools.
TOOLS = {
    "get_price": get_price,
    "order_status": order_status,
    "place_order": place_order,
}

# Change this to the exact model name shown by `ollama list`.
MODEL_NAME = "qwen3.5:0.8b"

llm = init_chat_model(
    MODEL_NAME,
    model_provider="ollama",
    temperature=0,
)

# Give the model the descriptions of our available tools.
llm_with_tools = llm.bind_tools(list(TOOLS.values()))

# Keep conversation messages as memory during this session.
messages = [
    {
        "role": "system",
        "content": (
            "You are the Sweet Crumbs bakery assistant. "
            "Use get_price for prices and order_status for order tracking. "
            "Use place_order only when the customer clearly asks to order. "
            "Ask for missing order details instead of guessing. "
            "Never invent prices or order statuses. "
            "Never claim an order was placed unless the tool confirms it. "
            "The owner must approve every new order. "
            "Answer in two short lines."
        ),
    }
]

print("Sweet Crumbs Agent is ready!")
print("Ask about prices, track an order, or place an order.")
print("Type 'bye' to exit.\n")

while True:
    user_text = input("You: ").strip()

    if user_text.lower() == "bye":
        print("Agent: Goodbye! Thank you for visiting Sweet Crumbs.")
        break

    if not user_text:
        continue

    messages.append({"role": "user", "content": user_text})

    # The agent loop continues until a final answer is produced.
    for step in range(MAX_STEPS):
        response = llm_with_tools.invoke(messages)

        # Preserve the model response so the tool requests stay in memory.
        messages.append(response)

        # No tool call means the model has answered normally.
        if not response.tool_calls:
            print(f"Agent: {response.text}\n")
            break

        # Python, not the model, executes each requested tool.
        for call in response.tool_calls:
            name = call["name"]
            args = call["args"]

            if name not in TOOLS:
                result = f"Error: unknown tool '{name}'."
            else:
                try:
                    result = TOOLS[name].invoke(args)
                except (ValidationError, ValueError, TypeError) as error:
                    result = (
                        f"Tool input error: {error}. "
                        "Check the tool's required arguments."
                    )

            print(f"[tool] {name}({args}) -> {result}")

            # Match the result to the exact tool request.
            messages.append(
                ToolMessage(
                    content=str(result),
                    tool_call_id=call["id"],
                )
            )

    else:
        # The loop's else runs only if no break occurred.
        print(
            "Agent: Sorry, I could not finish this request. "
            "Please ask the bakery owner for help.\n"
        )
