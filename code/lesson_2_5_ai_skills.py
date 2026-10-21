
"""Lesson 2.5: AI Skills Toolkit for a local business."""

from langchain.chat_models import init_chat_model

# Business name used in customer replies.
BUSINESS = "Sweet Crumbs"

# Create both AI models once, outside the functions.
# The precise model is used for factual tasks.
precise = init_chat_model(
    "qwen3.5:0.8b",
    model_provider="ollama",
    temperature=0.2
)

# The creative model is used for customer replies.
creative = init_chat_model(
    "qwen3.5:0.8b",
    model_provider="ollama",
    temperature=0.8
)


def estimate_tokens(text: str) -> int:
    """Estimate tokens using about four characters per token."""
    return round(len(text) / 4)


def ask_ai(
    prompt: str,
    system: str = "You are a helpful assistant. Answer in 2 short lines.",
    creative_mode: bool = False
) -> str:
    """Send a prompt to the AI and return its answer as text."""

    # Choose the model based on the task.
    if creative_mode:
        llm = creative
    else:
        llm = precise

    response = llm.invoke([
        {"role": "system", "content": system},
        {"role": "user", "content": prompt}
    ])

    return response.text.strip()


def summarize(text: str, max_words: int = 30) -> str:
    """Summarize text within the requested word limit."""
    prompt = f"Summarize in at most {max_words} words:\n{text}"
    return ask_ai(prompt)


def translate(text: str, language: str = "Urdu") -> str:
    """Translate text into the selected language."""
    prompt = (
        f"Translate the following text into {language}. "
        f"Reply with the translation only:\n{text}"
    )
    return ask_ai(prompt)


def reply_to_review(review: str, business: str) -> str:
    """Write a short, polite reply to a customer review."""
    prompt = (
        f"Write a polite 2-line reply from {business} "
        f"to this customer review:\n{review}"
    )
    return ask_ai(prompt, creative_mode=True)


# Test a function that does not need an AI call.
assert estimate_tokens("Hello AI") == 2
print("Function tests passed!")

# Count how often each skill is used.
usage = {
    "summarize": 0,
    "translate": 0,
    "reply": 0
}

print(f"\n{BUSINESS} AI Toolkit")
print("Commands: /summarize, /translate, /reply, bye")

while True:
    command = input("\nCommand: ").strip().lower()

    if command == "bye":
        break

    elif command == "/summarize":
        text = input("Text to summarize: ").strip()

        if text:
            result = summarize(text)
            print(f"AI: {result}")
            usage["summarize"] += 1
        else:
            print("Please enter some text.")

    elif command == "/translate":
        text = input("Text to translate: ").strip()

        if not text:
            print("Please enter some text.")
            continue

        language = input(
            "Language (press Enter for Urdu): "
        ).strip()

        if language == "":
            result = translate(text)
        else:
            result = translate(text, language)

        print(f"AI: {result}")
        usage["translate"] += 1

    elif command == "/reply":
        review = input("Customer review: ").strip()

        if review:
            result = reply_to_review(review, BUSINESS)
            print(f"AI: {result}")
            print(
                f"Estimated review tokens: "
                f"{estimate_tokens(review)}"
            )
            usage["reply"] += 1
        else:
            print("Please enter a customer review.")

    else:
        print(
            "Unknown command. Try /summarize, "
            "/translate, /reply or bye."
        )

# Display the usage summary after the user exits.
print("\nSkills used today:")

for skill, count in usage.items():
    print(f"  {skill}: {count}")

print("Goodbye!")
