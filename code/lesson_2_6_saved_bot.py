
"""Lesson 2.6: A saved bakery chatbot with JSON and error handling."""

import json
from pathlib import Path

import httpx
import ollama
from langchain.chat_models import init_chat_model

# Keep files inside the code folder, regardless of where we run the command.
BASE_DIR = Path(__file__).resolve().parent

FAQ_FILE = BASE_DIR / "faq.json"
HISTORY_FILE = BASE_DIR / "chat_history.json"
LOG_FILE = BASE_DIR / "errors.log"

# Use the Ollama model installed on your computer.
MODEL = "qwen3.5:0.8b"


def log_error(message):
    """Save an error message in the log file."""
    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(message + "\n")


# Load business information from JSON.
try:
    with open(FAQ_FILE, encoding="utf-8") as file:
        facts = json.load(file)

except FileNotFoundError:
    raise SystemExit(
        f"Missing {FAQ_FILE.name}. Please create code/faq.json first."
    )

except json.JSONDecodeError as error:
    raise SystemExit(
        f"Your FAQ JSON is invalid on line {error.lineno}."
    )

# Check that the essential business information exists.
if not all(key in facts for key in ("name", "city", "hours", "prices")):
    raise SystemExit(
        "faq.json must contain name, city, hours, and prices."
    )

# Create the AI model.
llm = init_chat_model(
    MODEL,
    model_provider="ollama"
)

# Give the AI its business facts and instructions.
system = {
    "role": "system",
    "content": (
        f"You are the assistant of {facts['name']} in {facts['city']}. "
        f"Business facts: {json.dumps(facts, ensure_ascii=False)}. "
        "Only use the supplied facts. Do not invent prices or services. "
        "If a fact is missing, say you do not have that information. "
        "Answer in two short lines."
    )
}

# Load previous messages if the history file exists.
messages = [system]

try:
    with open(HISTORY_FILE, encoding="utf-8") as file:
        old_messages = json.load(file)

    if isinstance(old_messages, list):
        # Keep only valid user and assistant messages.
        messages = [system] + [
            message
            for message in old_messages
            if isinstance(message, dict)
            and message.get("role") in ("user", "assistant")
            and isinstance(message.get("content"), str)
        ]

        print(f"Loaded {len(messages) - 1} old messages.")

    else:
        print("History format was invalid. Starting a fresh chat.")

except FileNotFoundError:
    print("No previous chat found. Starting a new chat.")

except json.JSONDecodeError as error:
    print(f"History file is damaged: {error}")
    print("Starting a fresh chat.")

except OSError as error:
    print(f"Could not read chat history: {error}")
    log_error(f"History read error: {error}")

print(f"\n{facts['name']} Bot")
print("Ask me about our bakery!")
print("Commands: /reset, bye")

# Keep chatting until the user types bye.
while True:
    try:
        user_text = input("\nYou: ").strip()

    except (EOFError, KeyboardInterrupt):
        print("\nBot: Goodbye!")
        break

    if user_text.lower() == "bye":
        print("Bot: Goodbye! Your chat is saved.")
        break

    if not user_text:
        continue

    if user_text.lower() == "/reset":
        messages = [system]

        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as file:
                json.dump([], file, indent=2, ensure_ascii=False)

            print("Bot: Memory cleared.")

        except OSError as error:
            print("Bot: I could not save the reset.")
            log_error(f"History reset error: {error}")

        continue

    # Add the user's question to the conversation.
    messages.append({
        "role": "user",
        "content": user_text
    })

    # Use the latest six messages while preserving the system instructions.
    conversation = [system] + messages[1:][-6:]

    try:
        response = llm.invoke(conversation)
        answer = response.text.strip()

        # Save only simple dictionaries, not the AI response object.
        messages.append({
            "role": "assistant",
            "content": answer
        })

        print(f"Bot: {answer}")

    except httpx.ConnectError:
        print(
            "Bot: Ollama is not running. Open the Ollama app "
            "and try again."
        )
        messages.pop()
        log_error("ConnectError: Could not connect to Ollama.")

    except ollama.ResponseError as error:
        print(
            "Bot: I could not use the selected AI model. "
            "Check your installed model with 'ollama list'."
        )
        messages.pop()
        log_error(f"Ollama ResponseError: {error}")

    except (ValueError, KeyError) as error:
        print("Bot: I had trouble processing that request.")
        messages.pop()
        log_error(f"Input/data error: {error}")

    except Exception as error:
        # Log unexpected errors instead of terminating the chat.
        print("Bot: Something went wrong. Please try again.")
        messages.pop()
        log_error(f"Unexpected error: {type(error).__name__}: {error}")

    # Save the chat after each successful AI response.
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as file:
            json.dump(
                messages[1:],
                file,
                indent=2,
                ensure_ascii=False
            )

    except OSError as error:
        print("Bot: I could not save your chat history.")
        log_error(f"History write error: {error}")
