
"""Choose an example AI model based on the user's task."""

task = input("Task (code / private / chat): ").strip().lower()
tokens = int(input("Estimated tokens: "))

# Private tasks should stay local when privacy is required.
if task == "private":
    model = "Ollama local model"
    price_per_1k_tokens = 0.0

elif task == "code":
    model = "Cloud coding model"
    price_per_1k_tokens = 2.0

elif task == "chat":
    model = "Budget cloud model"
    price_per_1k_tokens = 0.5

else:
    model = "Unknown task"
    price_per_1k_tokens = 0.0

# Reject invalid input rather than calculating a misleading cost.
if tokens < 0:
    print("Error: tokens cannot be negative.")
elif task not in ("code", "private", "chat"):
    print("Error: choose code, private, or chat.")
else:
    cost = tokens / 1000 * price_per_1k_tokens

    print("=" * 35)
    print(f"Chosen model: {model}")
    print(f"Estimated cost: {cost:.2f} example currency units")

    if tokens > 4000:
        print("Warning: consider shortening the request.")
    else:
        print("Length is fine.")
