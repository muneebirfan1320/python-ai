
"""
Lesson 2.3: Bakery bot that uses real facts and can switch personality.
"""

from langchain.chat_models import init_chat_model

# Store model settings in one dictionary
config = {
    "model": "llama3.2",
    "temperature": 0.3,
    "max_messages": 6
}

# Store real business facts in a dictionary
facts = {
    "name": "Sweet Crumbs",
    "city": "Lahore",
    "hours": "9 am to 10 pm",
    "prices": {
        "chocolate cake": 1500,
        "cupcake": 250,
        "brownie": 300
    }
}

# Define three personalities for the chatbot
personas = {
    "friendly": "warm and cheerful, uses simple words",
    "formal": "polite and professional, no jokes",
    "sales": "excited, always suggests one extra item to buy"
}

# Create the AI model once
llm = init_chat_model(
    config["model"],
    model_provider="ollama",
    temperature=config["temperature"]
)

# Give the AI real business facts to reduce made-up answers
rules = (
    f"You are the assistant of {facts['name']} bakery in {facts['city']}. "
    f"Opening hours: {facts['hours']}. "
    f"Prices in PKR: {facts['prices']}. "
    "Only use these facts. If you do not know an answer, "
    "say you will check with the manager. "
    "Answer in 2 short lines."
)

# Start with the friendly personality
style = personas["friendly"]

# Keep the system instructions at the beginning of the history
messages = [
    {
        "role": "system",
        "content": f"{rules} Your style: {style}."
    }
]

print("Sweet Crumbs Persona Bot")
print("Commands: /persona friendly|formal|sales, /price <item>, bye")

while True:
    # Get a message from the user
    text = input("\nYou: ").strip()

    # Exit the chatbot
    if text.lower() == "bye":
        print("Bot: Goodbye!")
        break

    # Change the chatbot's personality
    elif text.lower().startswith("/persona "):
        name = text[9:].strip().lower()

        # Use friendly as the fallback for an invalid personality
        if name in personas:
            style = personas[name]
        else:
            style = personas["friendly"]
            name = "friendly"

        # Update the system message without losing its business facts
        messages[0]["content"] = f"{rules} Your style: {style}."

        print(f"Bot: Style changed to {name}.")

    # Answer price questions directly from the dictionary
    elif text.lower().startswith("/price "):
        item = text[7:].strip().lower()

        if item in facts["prices"]:
            print(
                f"Bot: {item.title()} costs "
                f"{facts['prices'][item]} PKR."
            )
        else:
            print(f"Bot: Sorry, {item} is not on our menu.")

    # Handle empty input
    elif text == "":
        print("Bot: Please type a message.")

    # Send normal questions to the AI
    else:
        # Save the user's message
        messages.append({
            "role": "user",
            "content": text
        })

        # Keep the system message and the latest six chat messages
        messages = (
            [messages[0]]
            + messages[1:][-config["max_messages"]:]
        )

        try:
            # Ask the AI using the conversation history
            response = llm.invoke(messages)
            answer = response.text

            # Save the AI's reply so the bot remembers it
            messages.append({
                "role": "assistant",
                "content": answer
            })

            # Display the answer
            print(f"Bot: {answer}")

        except Exception as error:
            print(f"Bot: Something went wrong: {error}")
            print("Check that Ollama is running and the model is installed.")
