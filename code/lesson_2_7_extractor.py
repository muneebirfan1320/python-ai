
"""Lesson 2.7: Extract WhatsApp orders into checked JSON."""

import json
from pathlib import Path

from langchain.chat_models import init_chat_model

# Save the output inside the code folder.
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_FILE = BASE_DIR / "orders.json"

# These are the trusted prices. Python calculates all totals.
PRICES = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300
}

# Tell the AI the exact structure we expect.
ORDER_SCHEMA = {
    "type": "object",
    "properties": {
        "customer": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "quantity": {"type": "integer"}
                },
                "required": ["name", "quantity"]
            }
        },
        "address": {"type": "string"}
    },
    "required": ["customer", "items", "address"]
}

# Temperature 0 makes extraction more consistent.
extractor = init_chat_model(
    "qwen3.5:0.8b",
    model_provider="ollama",
    temperature=0,
    format=ORDER_SCHEMA
)

# Give the AI instructions and the approved menu.
SYSTEM = (
    "Extract orders from customer messages. "
    f"Allowed menu items: {', '.join(PRICES.keys())}. "
    "Return only items clearly requested by the customer. "
    "Do not invent names, addresses, quantities, or products. "
    "If the customer name or address is missing, use an empty string. "
    "If the message is not an order, return an empty items list. "
    "Use the exact menu item names when clearly identifiable. "
    "Quantities must be positive whole numbers."
)

# Add your own customer messages here.
messages_in = [
    "Salam! 2 cupcakes aur 1 chocolate cake chahiye. Ali, house 12 Gulberg",
    "3 brownies please, Sara, DHA phase 5",
    "Hi, do you deliver to Johar Town?",
    "I want five brownies. My name is Bilal, Model Town.",
    "2 pizzas and 1 brownie please."
]

saved = []

# Process every customer message.
for message in messages_in:
    print(f"\nMessage: {message}")

    try:
        response = extractor.invoke([
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": message}
        ])

        order = json.loads(response.text)

    except (json.JSONDecodeError, ValueError) as error:
        print(f"Could not read the AI response: {error}")
        continue

    # Check that the required fields exist and have the right types.
    if (
        not isinstance(order, dict)
        or not isinstance(order.get("customer"), str)
        or not isinstance(order.get("address"), str)
        or not isinstance(order.get("items"), list)
    ):
        print("Invalid order structure. Skipping this message.")
        continue

    items = order["items"]

    if not items:
        print("Not an order: needs a human reply.")
        continue

    total = 0
    problems = []
    valid_items = []

    # Validate each item and calculate its price in Python.
    for item in items:
        if not isinstance(item, dict):
            problems.append("Invalid item structure.")
            continue

        name = item.get("name")
        quantity = item.get("quantity")

        if not isinstance(name, str):
            problems.append("Item name is invalid.")
            continue

        name = name.strip().lower()

        if name not in PRICES:
            problems.append(f"'{name}' is not on our menu.")
            continue

        # bool is a subclass of int in Python, so reject it explicitly.
        if (
            isinstance(quantity, bool)
            or not isinstance(quantity, int)
            or quantity <= 0
        ):
            problems.append(f"Invalid quantity for '{name}'.")
            continue

        # Calculate using trusted prices, never an AI-generated price.
        line_total = PRICES[name] * quantity
        total += line_total

        valid_items.append({
            "name": name,
            "quantity": quantity,
            "unit_price": PRICES[name],
            "line_total": line_total
        })

        print(
            f"  {quantity} x {name} = {line_total} PKR"
        )

    customer = order["customer"].strip()
    address = order["address"].strip()

    # Flag a customer name that does not appear in the original message.
    if customer and customer.casefold() not in message.casefold():
        problems.append(
            f"Customer '{customer}' does not appear in the message. "
            "Please check manually."
        )

    # Save valid, menu-matched items and their calculated totals.
    if not valid_items:
        print("No valid menu items found. Order needs manual review.")
        for problem in problems:
            print(f"  CHECK: {problem}")
        continue

    checked_order = {
        "customer": customer,
        "items": valid_items,
        "address": address,
        "total": total,
        "problems": problems,
        "needs_review": bool(problems)
    }

    saved.append(checked_order)

    print(f"  Customer: {customer or '(missing)'}")
    print(f"  Address: {address or '(missing)'}")
    print(f"  Total: {total} PKR")

    for problem in problems:
        print(f"  CHECK: {problem}")

# Save the extracted orders to a JSON file.
try:
    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(
            saved,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"\nSaved {len(saved)} orders to {OUTPUT_FILE.name}")

except OSError as error:
    print(f"Could not save orders: {error}")
