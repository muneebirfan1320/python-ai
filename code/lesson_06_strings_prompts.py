
"""Clean a user's question and build a prompt for an AI tutor."""

# Clean names so the greeting looks professional.
name = input("Enter your name: ").strip().title()

# Clean the question so extra spaces do not remain at its edges.
question = input("Enter your question: ").strip().capitalize()

character_count = len(question)

# This is only a rough estimate; actual token counts vary by text and model.
estimated_tokens = round(character_count / 4)

# Check in lowercase so Python, PYTHON, and python all match.
mentions_python = "python" in question.lower()

short_question = question[:150]

prompt = f"""You are a helpful Python tutor.
Hello, {name}!
Answer in simple English with one example.
Question: {short_question}"""

print("\n" + "=" * 40)
print(f"Name: {name}")
print(f"Cleaned question: {question}")
print(f"Characters: {character_count}")
print(f"Estimated tokens: {estimated_tokens}")
print(f"Mentions Python: {mentions_python}")
print("=" * 40)
print("AI Prompt:")
print(prompt)
