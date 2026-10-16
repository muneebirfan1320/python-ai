
"""Build a useful AI prompt from a business owner's answers."""

# Personalizing the greeting makes the tool feel designed for each user.
name = input("Your name: ")

business = input("Business type: ")

# A specific problem helps the AI generate more relevant solutions.
problem = input("Biggest problem: ")

print(f"\nWelcome, {name}!")

prompt = (
    f"Suggest 3 AI solutions for a {business} "
    f"that struggles with {problem}."
)

print("--- Your AI Prompt ---")
print(prompt)
