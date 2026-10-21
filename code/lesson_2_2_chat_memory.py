
"""
Lesson 2.2: Personal Tutor with Memory
A chatbot that remembers recent messages.
"""

from langchain.chat_models import init_chat_model
import time

# Keep the system instructions and the latest 6 messages
MAX_MESSAGES = 6

# Create the AI model once
llm = init_chat_model(
    "llama3.2",
    model_provider="ollama",
    temperature=0.2
)

# Store the system message at the beginning of the history
messages = [
    {
        "role": "system",
        "content": (
            "You are a friendly personal tutor. "
            "Explain topics in simple language for a beginner. "
            "Give clear and short answers."
        )
    }
]

print("Personal Tutor with Memory")
print("Commands: /reset, /count, bye")

while True:
    # Get a message from the user
    text = input("\nYou: ").strip()

    # Exit the chatbot
    if text.lower() == "bye":
        print("Tutor: Goodbye! Keep learning.")
        break

    # Clear chat history but keep system instructions
    elif text.lower() == "/reset":
        messages = [messages[0]]
        print("Tutor: Memory cleared.")
        continue

    # Show the number of messages currently stored
    elif text.lower() == "/count":
        print(f"Tutor: {len(messages) - 1} chat messages stored.")
        continue

    # Do not send empty messages to the AI
    elif text == "":
        print("Tutor: Please type a question.")
        continue

    # Save the user's message
    messages.append({
        "role": "user",
        "content": text
    })

    # Keep the system message and the latest 6 chat messages
    messages = [messages[0]] + messages[1:][-MAX_MESSAGES:]

    try:
        # Start measuring response time
        start_time = time.perf_counter()

        # Send conversation history to the AI
        response = llm.invoke(messages)

        # Calculate response time
        elapsed = time.perf_counter() - start_time

        # Get the AI's answer
        answer = response.text

        # Save the AI's answer in chat history
        messages.append({
            "role": "assistant",
            "content": answer
        })

        # Show the answer
        print(f"Tutor: {answer}")

        # Show token usage
        usage = response.usage_metadata or {}
        input_tokens = usage.get("input_tokens", 0)
        output_tokens = usage.get("output_tokens", 0)

        print(
            f"(Input tokens: {input_tokens} | "
            f"Output tokens: {output_tokens} | "
            f"Time: {elapsed:.2f} seconds)"
        )

    except Exception as error:
        print(f"Tutor: Something went wrong: {error}")
        print("Check that Ollama is running and your model is installed.")
