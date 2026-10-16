
"""Create an AI model profile and estimate token costs."""

# Use clear settings so the model configuration is easy to understand.
model_name: str = "qwen3.5:0.8b"
context_window: int = 4096
price_per_1k_tokens: float = 0.5
runs_locally: bool = True

print("--- AI Model Profile ---")
print(f"Model: {model_name} ({type(model_name).__name__})")
print(f"Context window: {context_window} ({type(context_window).__name__})")
print(f"Price per 1K tokens: {price_per_1k_tokens} ({type(price_per_1k_tokens).__name__})")
print(f"Runs locally: {runs_locally} ({type(runs_locally).__name__})")

# Convert input to an integer because token counts are whole numbers.
tokens_used = int(input("How many tokens does one chat use? "))

cost = tokens_used / 1000 * price_per_1k_tokens

print(f"Estimated cost per chat: {cost:.2f} example currency units")
