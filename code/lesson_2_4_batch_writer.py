
"""Lesson 2.4: Write a short AI description for every product."""

from langchain.chat_models import init_chat_model
import time

# Create the AI model once, outside the loop.
# Use the model you have installed in Ollama.
writer = init_chat_model(
    "qwen3.5:0.8b",
    model_provider="ollama",
    temperature=0.7
)

# Product names and prices in PKR.
products = {
    "chocolate cake": 1500,
    "cupcake": 250,
    "brownie": 300,
    "old stock": 0,
    "donut": 200
}

# Store descriptions and totals before the loop begins.
results = []
total_tokens = 0
total_seconds = 0

# Generate a description for each product.
for name, price in products.items():

    # Skip products that are not for sale.
    if price == 0:
        print(f"Skipping {name} (no price)")
        continue

    # Ask AI to write a short product description.
    prompt = (
        f"Write one tempting sentence (maximum 15 words) "
        f"for '{name}' at {price} PKR, for a Lahore bakery menu. "
        f"Do not invent extra prices or business facts."
    )

    start_time = time.perf_counter()

    response = writer.invoke([
        {"role": "user", "content": prompt}
    ])

    elapsed = time.perf_counter() - start_time

    # Save the product information and AI description.
    results.append({
        "item": name,
        "price": price,
        "text": response.text.strip()
    })

    # Add this response's token count to the total.
    usage = response.usage_metadata or {}
    total_tokens += usage.get("total_tokens", 0)

    # Add the time taken for this AI call.
    total_seconds += elapsed

# Print all generated descriptions.
print("=" * 50)

for number, row in enumerate(results, start=1):
    print(f"{number}. {row['item'].title()} ({row['price']} PKR)")
    print(f"   {row['text']}")

print("=" * 50)

# Display the final summary.
print(f"{len(results)} descriptions generated")
print(f"Total tokens: {total_tokens}")
print(f"Total time: {total_seconds:.1f} seconds")
