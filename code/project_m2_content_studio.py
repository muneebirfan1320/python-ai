
"""
Module 2 Checkpoint 1: AI Content Studio
Creates bakery menu descriptions, social posts, price answers,
and a memory-based customer chatbot for Sweet Crumbs in Lahore.
"""

import time
from langchain.chat_models import init_chat_model

# Why: Keep model settings together so the business can change them easily.
config = {
    "model": "ollama:llama3.2",
    "max_messages": 8,
    "precise_temperature": 0.2,
    "creative_temperature": 0.8,
    "cloud_price_per_1k_tokens": 0.50
}

# Why: Real business facts prevent the AI from inventing prices and policies.
facts = {
    "name": "Sweet Crumbs",
    "type": "Bakery",
    "city": "Lahore",
    "hours": "9 am to 10 pm",
    "delivery_fee": 200,
    "free_delivery_minimum": 3000,
    "customers": "Families and university students",
    "prices": {
        "Chocolate Cake": 1500,
        "Cupcake": 250,
        "Brownie": 300,
        "Mango Tart": 0
    }
}

tones = {
    "fun": "Playful and full of energy, with short sentences.",
    "premium": "Elegant and calm, focused on quality.",
    "urgent": "Exciting and time-sensitive, but never invent a deadline."
}

# Why: Precise answers suit customer questions; creative answers suit marketing.
precise = init_chat_model(
    config["model"],
    temperature=config["precise_temperature"]
)
creative = init_chat_model(
    config["model"],
    temperature=config["creative_temperature"]
)

system_message = {
    "role": "system",
    "content": f"""
You are the customer assistant for {facts['name']}.
Business facts: {facts}
Only use these facts. Never invent prices, products, opening hours,
delivery rules, ingredients or promotions.
If the facts do not contain an answer, say you do not know.
Keep answers polite and concise.
"""
}

messages = [system_message]

menu_descriptions = []
chat_answers = 0
posts = 0
price_answers = 0
total_tokens = 0
total_seconds = 0.0

print("=" * 50)
print(f"   {facts['name']} AI Content Studio")
print("=" * 50)
print("Commands: /menu, /post fun|premium|urgent, /price <item>, /reset, bye")

while True:
    user_text = input("You: ").strip()

    # Why: Empty input should not trigger an unnecessary AI request.
    if not user_text:
        print("Studio: Please enter a question or command.")
        continue

    command_text = user_text.lower()

    if command_text == "bye":
        print("Studio: Goodbye!")
        break

    elif command_text == "/reset":
        # Why: Keep the system message so business rules remain active.
        messages = [system_message]
        print("Studio: Chat memory cleared.")

    elif command_text == "/menu":
        menu_descriptions = []

        for item, price in facts["prices"].items():
            # Why: A zero price means coming soon, so no AI call is needed.
            if price == 0:
                print(f"Studio: Skipping {item.lower()} (coming soon)")
                continue

            prompt = (
                f"Write one appealing sentence for the menu item {item}, "
                f"priced at {price:,} PKR, for {facts['name']} in "
                f"{facts['city']}. Only use the supplied facts. "
                "Do not invent ingredients or unsupported claims."
            )

            start = time.perf_counter()
            response = creative.invoke(prompt)
            elapsed = time.perf_counter() - start

            usage = response.usage_metadata or {}
            total_tokens += usage.get("total_tokens", 0)
            total_seconds += elapsed

            menu_descriptions.append({
                "item": item,
                "price": price,
                "text": response.text
            })

        print("-" * 50)
        for number, product in enumerate(menu_descriptions, start=1):
            print(f"{number}. {product['item']} ({product['price']:,} PKR)")
            print(f"   {product['text']}")
        print("-" * 50)

    elif command_text.startswith("/post"):
        parts = user_text.split(maxsplit=1)
        requested_tone = parts[1].strip().lower() if len(parts) > 1 else ""

        # Why: get() provides a safe default for unknown tone names.
        tone_description = tones.get(
            requested_tone,
            tones["fun"]
        )
        selected_tone = (
            requested_tone if requested_tone in tones else "fun"
        )

        prompt = f"""
Write one social media post for {facts['name']}, a bakery in {facts['city']}.
Tone: {tone_description}
Opening hours: {facts['hours']}.
Menu and prices: {facts['prices']}.
Delivery fee: {facts['delivery_fee']} PKR.
Free delivery on orders from {facts['free_delivery_minimum']} PKR.
Only use these facts. Do not invent ingredients, discounts or deadlines.
Keep it suitable for Instagram.
"""

        print(f"Studio ({tone_description}):")
        start = time.perf_counter()

        for chunk in creative.stream(prompt):
            if chunk.content:
                print(chunk.content, end="", flush=True)

            # Some streaming integrations provide usage on the final chunk.
            usage = chunk.usage_metadata or {}
            total_tokens += usage.get("total_tokens", 0)

        elapsed = time.perf_counter() - start
        total_seconds += elapsed
        posts += 1
        print()

    elif command_text.startswith("/price"):
        parts = user_text.split(maxsplit=1)
        requested_item = parts[1].strip().lower() if len(parts) > 1 else ""

        # Why: The dictionary gives exact prices without any AI cost.
        price = None
        matched_item = ""

        for item, item_price in facts["prices"].items():
            if item.lower() == requested_item:
                price = item_price
                matched_item = item
                break

        price_answers += 1

        if not requested_item:
            print("Studio: Please provide an item, for example /price cupcake.")
        elif price is None:
            print(f"Studio: Sorry, {requested_item.title()} is not on our menu.")
        elif price == 0:
            print(f"Studio: {matched_item} is coming soon.")
        else:
            print(f"Studio: {matched_item} costs {price:,} PKR.")

    else:
        messages.append({"role": "user", "content": user_text})

        # Keep the system message and only the recent conversation messages.
        messages = [messages[0]] + messages[1:][-config["max_messages"]:]

        start = time.perf_counter()
        response = precise.invoke(messages)
        elapsed = time.perf_counter() - start

        messages.append({
            "role": "assistant",
            "content": response.text
        })

        # Trim again so memory stays within the configured limit.
        messages = [messages[0]] + messages[1:][-config["max_messages"]:]

        usage = response.usage_metadata or {}
        input_tokens = usage.get("input_tokens", 0)
        total_tokens += usage.get("total_tokens", 0)
        total_seconds += elapsed
        chat_answers += 1

        print(f"Studio: {response.text}")
        print(
            f"        (memory: {len(messages)} messages, "
            f"{input_tokens} tokens sent)"
        )

print("=" * 50)
print("Session report")
print(
    f"Chat answers: {chat_answers} | "
    f"Menu descriptions: {len(menu_descriptions)} | "
    f"Posts: {posts} | Price answers: {price_answers}"
)
print(f"AI usage: {total_tokens:,} tokens in {total_seconds:.1f} seconds")
print("=" * 50)
