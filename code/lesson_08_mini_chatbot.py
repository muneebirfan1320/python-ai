
"""A rule-based chatbot for a sample bakery business."""

BOT = "Sweet Crumbs Bot"

print(f"{BOT}: Welcome! Ask me about prices, hours, location, or orders.")
print(f"{BOT}: Type 'bye' to exit or 'human' to request help.")

# Memory: ask for the customer's name only once.
name = input(f"{BOT}: What is your name? ").strip().title()

if not name:
    name = "Friend"

print(f"{BOT}: Nice to meet you, {name}!")

message_count = 0
unanswered_count = 0
complaint_count = 0

while True:
    message = input(f"{name}: ").strip().lower()
    message_count += 1

    # Why: check exit commands first so the loop can end.
    if message in ("bye", "exit"):
        print(f"{BOT}: Goodbye, {name}!")
        break

    # Why: complaints must be handled before ordinary order questions.
    elif any(word in message for word in ("complaint", "refund", "late")):
        complaint_count += 1
        print(f"{BOT}: Sorry about that. A manager will help you.")

    # Stretch goal: finish the chat when human help is requested.
    elif "human" in message or "agent" in message:
        print(f"{BOT}: Connecting you to a human...")
        break

    elif not message:
        print(f"{BOT}: Please type a question.")

    elif message in ("hi", "hello") or message.startswith("salam"):
        print(f"{BOT}: Hello, {name}! How can I help?")

    elif any(word in message for word in ("hour", "open", "time")):
        print(f"{BOT}: We are open from 9 am to 10 pm every day.")

    elif any(word in message for word in ("price", "cost", "how much")):
        print(f"{BOT}: Cakes start at 1,500 PKR. Cupcakes cost 250 PKR each.")

    elif any(word in message for word in ("where", "location", "address")):
        print(f"{BOT}: Our example location is Main Boulevard, Lahore.")

    elif "order" in message or "delivery" in message:
        print(f"{BOT}: Delivery is free on orders above 3,000 PKR.")

    else:
        unanswered_count += 1

        # Why: unknown questions show where the rules need improvement.
        prompt = (
            "You are a helpful bakery assistant. "
            f"Answer this customer question in 2 lines: {message}"
        )

        print(f"{BOT}: I don't know that answer yet.")
        print(f"Future AI prompt: {prompt}")

print("=" * 40)
print(f"Chat summary for {name}")
print(f"Messages received: {message_count}")
print(f"Unanswered questions: {unanswered_count}")
print(f"Complaints received: {complaint_count}")
print("Thank you for using the bot!")
